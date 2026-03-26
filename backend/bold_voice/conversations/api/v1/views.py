import logging
import random
import string

from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch, OuterRef, Subquery, DateTimeField, CharField, Count
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bold_voice.conversations.api.v1.exceptions import AudioAnalysisFailed
from bold_voice.conversations.api.v1.filters import VoiceChatFilter
from bold_voice.conversations.api.v1.pagination import DefaultPagination
from bold_voice.conversations.api.v1.serializers.bookmark import PracticeTextBookmarkSerializer
from bold_voice.conversations.api.v1.serializers.category import CategorySerializer
from bold_voice.conversations.api.v1.serializers.phoneme import (
    PhonemeCategorySerializer,
    PhonemeDetailSerializer,
    PhonemeListSerializer
)
from bold_voice.conversations.api.v1.serializers.practice import (
    PracticeSpeakingTextSerializer,
    PracticeSpeakingTextResponseSerializer
)
from bold_voice.conversations.api.v1.serializers.scenario import ScenarioSerializer
from bold_voice.conversations.api.v1.serializers.speech_scan import (
    SpeechScanSessionListSerializer,
    SpeechScanSessionDetailSerializer,
    SpeechScanSessionPracticeTextSerializer
)
from bold_voice.conversations.api.v1.serializers.voice_chat import (
    VoiceChatListSerializer,
    VoiceChatCreateSerializer,
    VoiceChatDetailSerializer
)
from bold_voice.conversations.api.v1.serializers.voice_message import (
    VoiceMessageDetailSerializer,
    VoiceMessageCreateSerializer,
    VoiceMessagePracticeWordSerializer
)
from bold_voice.conversations.models import (
    Character,
    Scenario,
    Category,
    VoiceChat,
    VoiceMessage,
    VoiceChatScore,
    VoiceMessageScore,
    PhonemeCategory,
    Phoneme,
    PhonemeExample,
    PracticeTextBookmark, SpeechScanSession, SpeechScanConfig, SpeechScanSessionScoreDetail
)
from bold_voice.conversations.services.ai_services import get_ai_transcript, get_ai_audio_analysis
from bold_voice.conversations.services.speaking_practice import SpeakingPracticeService
from bold_voice.conversations.utils import (
    generate_random_color,
)

logger = logging.getLogger(__name__)


class AppConfigAPIView(APIView):
    """
    API View to return environment variables used in the application.
    """
    permission_classes = []

    def get(self, request):
        try:
            response_data = {
                'VOICECHAT_MESSAGE_LIMIT': settings.VOICECHAT_MESSAGE_LIMIT,
                'PERFECT_WORD_MIN_SCORE': settings.PERFECT_WORD_MIN_SCORE,
                'WEAK_WORD_MAX_SCORE': settings.WEAK_WORD_MAX_SCORE,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            raise APIException(
                detail=_(str(e)),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = []
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']
    pagination_class = None

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            voicechat_prefetch = Prefetch(
                'voice_chats',
                queryset=VoiceChat.objects.filter(user=user).annotate(message_count=Count('voice_messages')),
                to_attr='user_voice_chats'
            )
        else:
            voicechat_prefetch = Prefetch(
                'voice_chats',
                queryset=VoiceChat.objects.none(),
                to_attr='user_voice_chats'
            )

        return Category.objects.order_by('sort_order').prefetch_related(
            Prefetch(
                'scenarios',
                queryset=Scenario.objects.order_by('sort_order').prefetch_related(
                    Prefetch(
                        'character',
                        queryset=Character.objects.all()
                    ),
                    voicechat_prefetch
                )
            )
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['message_limit'] = settings.VOICECHAT_MESSAGE_LIMIT
        return context


class ScenarioViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = []
    queryset = Scenario.objects.order_by('sort_order').select_related('category', 'character').all()
    serializer_class = ScenarioSerializer
    filter_backends = []
    pagination_class = None

    @action(
        detail=False,
        methods=['get'],
        url_path='random'
    )
    def random(self, request):
        ids = self.get_queryset().values_list('id', flat=True)
        if not ids.exists():
            return Response(
                {"detail": _("No scenarios available.")},
                status=status.HTTP_404_NOT_FOUND
            )

        random_id = random.choice(list(ids))

        instance = self.get_queryset().get(id=random_id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class VoiceChatViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = VoiceChatFilter
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return VoiceChatListSerializer
        if self.action == 'create':
            return VoiceChatCreateSerializer
        if self.action == 'messages':
            return VoiceMessageCreateSerializer
        if self.action == 'practice_word':
            return VoiceMessagePracticeWordSerializer
        return VoiceChatDetailSerializer

    def get_queryset(self):
        if self.action == 'list':
            latest_message_qs = VoiceMessage.objects.filter(
                voice_chat=OuterRef('pk')
            ).order_by('-created_at')

            return (
                VoiceChat.objects.filter(user=self.request.user)
                .select_related('scenario', 'score_record')
                .annotate(
                    last_message_created_at=Subquery(
                        latest_message_qs.values('created_at')[:1],
                        output_field=DateTimeField()
                    ),
                    last_message_transcript=Subquery(
                        latest_message_qs.values('transcript')[:1],
                        output_field=CharField()
                    )
                )
                .order_by('-last_message_created_at')
            )
        if self.action == 'retrieve':
            return (
                VoiceChat.objects.filter(user=self.request.user)
                .select_related('scenario', 'character')
                .prefetch_related(
                    Prefetch(
                        'voice_messages',
                        queryset=VoiceMessage.objects.select_related('score_record').order_by('id'),
                    )
                )
            )
        return VoiceChat.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        scenario = serializer.validated_data.get("scenario")

        character = scenario.character if scenario else None
        gradient_start_color = generate_random_color()
        gradient_end_color = generate_random_color()

        with transaction.atomic():
            voicechat = serializer.save(
                user=self.request.user,
                character=character,
                gradient_start_color=gradient_start_color,
                gradient_end_color=gradient_end_color
            )

            title = scenario.title if scenario else None
            context = scenario.description if scenario else None
            ai_role = scenario.character_role if scenario else None

            if len(scenario.initial_texts) > 0:
                transcript = random.choice(scenario.initial_texts)
            else:
                transcript = get_ai_transcript(
                    title=title,
                    context=context,
                    ai_role=ai_role,
                    ai_character=character,
                    scenario_type=scenario.category.type,
                    voice_chat=voicechat
                )

            VoiceMessage.objects.create(
                voice_chat=voicechat,
                role=VoiceMessage.Role.ASSISTANT,
                transcript=transcript,
            )

    @extend_schema(
        request=VoiceChatCreateSerializer,
        responses=VoiceChatDetailSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            VoiceChatDetailSerializer(
                serializer.instance, context={'request': request, "voice_chat": serializer.instance}
            ).data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            context={'request': request, "voice_chat": instance}
        )
        return Response(serializer.data)

    def create_voice_message(self, serializer, voice_chat):
        role = serializer.validated_data.get("role")

        with transaction.atomic():
            if role == VoiceMessage.Role.USER:
                voice_message = serializer.save(voice_chat=voice_chat, role=VoiceMessage.Role.USER)

                # Call AI scoring function
                try:
                    data = get_ai_audio_analysis(voice_message.audio_file)
                except RuntimeError as e:
                    raise APIException(
                        detail=_(str(e)),
                        code=status.HTTP_503_SERVICE_UNAVAILABLE
                    )

                if data.get("num_words_spoken") == 0:
                    raise serializers.ValidationError(
                        {
                            "detail": _("No words spoken in the audio message. Please try again.")
                        }
                    )

                # Update the VoiceMessage
                voice_message.transcript = data.get("transcript")
                voice_message.save()

                word_infos = data.get("word_list_serializable")
                suggested_words = []
                existing_words = set()

                for word_info in word_infos:
                    word_text = word_info['word'].strip(string.punctuation)
                    if word_info.get("score") < settings.WEAK_WORD_MAX_SCORE and word_text not in existing_words:
                        suggested_words.append({
                            'word': word_text,
                            'score': 0,
                        })
                        existing_words.add(word_text)

                # Create a VoiceMessageScore record
                VoiceMessageScore.objects.create(
                    voice_message=voice_message,
                    score=data.get("score"),
                    words=word_infos,
                    suggested_words=suggested_words,
                )

                # Update or create the VoiceChatScore
                voice_chat_score, is_created = VoiceChatScore.objects.get_or_create(voice_chat=voice_chat)
                voice_chat_score.total_word_score += data.get("total_word_score")
                voice_chat_score.num_words_spoken += data.get("num_words_spoken")
                voice_chat_score.num_perfect_words += data.get("num_perfect_words")
                voice_chat_score.time_spoken += data.get("time_spoken")

                # Recalculate ai_score only if num_words_spoken is not zero
                if voice_chat_score.num_words_spoken > 0:
                    voice_chat_score.ai_score = voice_chat_score.total_word_score / voice_chat_score.num_words_spoken
                else:
                    voice_chat_score.ai_score = 0

                voice_chat_score.save()
            else:
                title = voice_chat.scenario.title if voice_chat.scenario else None
                context = voice_chat.scenario.description if voice_chat.scenario else None
                ai_role = voice_chat.scenario.character_role if voice_chat.scenario else None

                try:
                    # Generate AI response
                    ai_response = get_ai_transcript(
                        title=title,
                        context=context,
                        ai_role=ai_role,
                        ai_character=voice_chat.scenario.character,
                        scenario_type=voice_chat.scenario.category.type,
                        voice_chat=voice_chat
                    )
                except RuntimeError as e:
                    raise APIException(
                        detail=_(str(e)),
                        code=status.HTTP_503_SERVICE_UNAVAILABLE
                    )

                # Save AI response as a VoiceMessage
                ai_message = VoiceMessage.objects.create(
                    voice_chat=voice_chat,
                    role=VoiceMessage.Role.ASSISTANT,
                    transcript=ai_response,
                )

                # Set the instance to return the AI message in response
                serializer.instance = ai_message

    @extend_schema(
        request=VoiceMessageCreateSerializer,
        responses=VoiceMessageDetailSerializer
    )
    @action(
        detail=True,
        methods=['post'],
        url_path='messages'
    )
    def messages(self, request, pk=None):
        voice_chat = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.create_voice_message(serializer, voice_chat)

        response_data = VoiceMessageDetailSerializer(
            serializer.instance,
            context={'request': request}
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=VoiceMessagePracticeWordSerializer,
        responses=PracticeSpeakingTextResponseSerializer
    )
    @action(
        detail=True,
        methods=['post'],
        url_path='messages/practice-word'
    )
    def practice_word(self, request, pk=None):
        """
        Endpoint to handle practice suggested words.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            voice_message_score = data['voice_message_score']
            suggested_word_index = data['suggested_word_index']
            suggested_word = voice_message_score.suggested_words[suggested_word_index].get('word')

            speaking_practice_service = SpeakingPracticeService(
                audio_file=data.get('audio_file'),
                reference_text=suggested_word
            )
            analysis_data = speaking_practice_service.analyze()

            voice_message_score.suggested_words[suggested_word_index]['score'] = analysis_data.get('score')
            voice_message_score.save(
                update_fields=['suggested_words']
            )

            return Response(
                PracticeSpeakingTextResponseSerializer(analysis_data).data,
                status=status.HTTP_200_OK
            )

        except AudioAnalysisFailed as e:
            raise APIException(
                detail=_(str(e)),
                code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except RuntimeError as e:
            raise APIException(
                detail=_(str(e)),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"detail": _(str(e))},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PhonemeCategoryViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = []
    serializer_class = PhonemeCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['phoneme_type']
    pagination_class = None

    def get_queryset(self):
        return (
            PhonemeCategory.objects
            .order_by('sort_order')
            .prefetch_related(
                Prefetch(
                    'phonemes',
                    queryset=Phoneme.objects.order_by('sort_order').prefetch_related(
                        Prefetch(
                            'examples',
                            queryset=PhonemeExample.objects.order_by('sort_order')
                        )
                    )
                )
            )
        )


class PhonemeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PhonemeDetailSerializer
        return PhonemeListSerializer

    def get_queryset(self):
        return (
            Phoneme.objects
            .order_by('sort_order')
            .prefetch_related(
                Prefetch(
                    'examples',
                    queryset=PhonemeExample.objects.order_by('sort_order')
                ),
                'confused_phonemes__examples',
            )
        )


class PracticeSpeakingTextAPIView(APIView):
    """
    API View for handling practice text and audio.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PracticeSpeakingTextSerializer

    @extend_schema(
        request=PracticeSpeakingTextSerializer,
        responses=PracticeSpeakingTextResponseSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            speaking_practice_service = SpeakingPracticeService(
                audio_file=data.get('audio'),
                reference_text=data.get('text')
            )
            response_data = speaking_practice_service.analyze()
            return Response(
                PracticeSpeakingTextResponseSerializer(response_data).data,
                status=status.HTTP_200_OK
            )

        except AudioAnalysisFailed as e:
            raise APIException(
                detail=_(str(e)),
                code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except RuntimeError as e:
            raise APIException(
                detail=_(str(e)),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            raise APIException(
                detail=_(str(e)),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PracticeTextBookmarkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookmarks of practice text.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticated]
    serializer_class = PracticeTextBookmarkSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'practice_text': ['exact'],
    }
    pagination_class = DefaultPagination

    def get_queryset(self):
        return PracticeTextBookmark.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        serializer.save(attempt_count=instance.attempt_count + 1)


class SpeechScanSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing speech scan sessions.
    """
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SpeechScanSessionDetailSerializer
        if self.action == 'practice_text':
            return SpeechScanSessionPracticeTextSerializer
        return SpeechScanSessionListSerializer

    def get_queryset(self):
        return (
            SpeechScanSession.objects.filter(user=self.request.user)
            .select_related('speech_scan_config')
            .prefetch_related(
                Prefetch(
                    'score_details',
                    queryset=SpeechScanSessionScoreDetail.objects.order_by('practice_text_index')
                )
            )
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        speech_scan_config = SpeechScanConfig.objects.filter(is_active=True).first()
        if not speech_scan_config:
            raise serializers.ValidationError(
                {"detail": _("No active speech scan configuration found.")}
            )
        serializer.save(user=self.request.user, speech_scan_config=speech_scan_config)

    @extend_schema(
        request=SpeechScanSessionListSerializer,
        responses=SpeechScanSessionDetailSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        detail_serializer = SpeechScanSessionDetailSerializer(
            serializer.instance,
            context={'request': request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=SpeechScanSessionPracticeTextSerializer,
        responses=PracticeSpeakingTextResponseSerializer
    )
    @action(
        detail=True,
        methods=['post'],
        url_path='practice-text'
    )
    def practice_text(self, request, pk=None):
        speech_scan_session = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={
                'request': request,
                'speech_scan_session': speech_scan_session
            }
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            audio_file = data.get('audio_file')
            practice_text_index = data.get('practice_text_index')
            speech_scan_config = speech_scan_session.speech_scan_config
            reference_text = (speech_scan_config.practice_texts[practice_text_index]['sentence'])

            speaking_practice_service = SpeakingPracticeService(
                audio_file=audio_file,
                reference_text=reference_text
            )
            analysis_data = speaking_practice_service.analyze()

            score_detail = speech_scan_session.score_details.filter(practice_text_index=practice_text_index).first()
            if score_detail:
                score_detail.score = analysis_data.get('score')
                score_detail.word_scores = analysis_data.get('word_scores')
                score_detail.audio_file = audio_file
                score_detail.save()

            else:
                speech_scan_session.score_details.create(
                    practice_text_index=practice_text_index,
                    score=analysis_data.get('score'),
                    word_scores=analysis_data.get('word_scores'),
                    audio_file=audio_file
                )

            speech_scan_session.update_scores_and_words()

            return Response(
                PracticeSpeakingTextResponseSerializer(analysis_data).data,
                status=status.HTTP_200_OK
            )

        except AudioAnalysisFailed as e:
            raise APIException(
                detail=_(str(e)),
                code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            raise APIException(
                detail=_(str(e)),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
