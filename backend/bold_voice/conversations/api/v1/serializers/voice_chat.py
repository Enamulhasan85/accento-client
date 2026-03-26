from rest_framework import serializers

from bold_voice.conversations.api.v1.serializers.character import CharacterSerializer
from bold_voice.conversations.api.v1.serializers.voice_message import VoiceMessageDetailSerializer
from bold_voice.conversations.models import Scenario, VoiceChat, VoiceChatScore, VoiceMessage


class SimpleScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ["id", "title", "description", "character_role", "icon", ]


class SimpleVoiceChatScoreSerializer(serializers.ModelSerializer):
    user_message_count = serializers.SerializerMethodField()
    class Meta:
        model = VoiceChatScore
        fields = [
            "id",
            "ai_score",
            "total_word_score",
            "num_words_spoken",
            "num_perfect_words",
            "time_spoken",
            "user_message_count",
            "feedback"
        ]

    def get_user_message_count(self, obj):
        return obj.voice_chat.voice_messages.filter(role=VoiceMessage.Role.USER).count()


class VoiceChatListSerializer(serializers.ModelSerializer):
    scenario = SimpleScenarioSerializer(read_only=True)
    score_record = SimpleVoiceChatScoreSerializer(read_only=True)
    last_message_created_at = serializers.DateTimeField()
    last_message_transcript = serializers.CharField()

    class Meta:
        model = VoiceChat
        fields = [
            "id",
            "scenario",
            "gradient_start_color",
            "gradient_end_color",
            "last_message_created_at",
            "last_message_transcript",
            "started_at",
            "completed_at",
            "score_record"
        ]


class VoiceChatDetailSerializer(serializers.ModelSerializer):
    character = CharacterSerializer(read_only=True)
    scenario = SimpleScenarioSerializer(read_only=True)
    voice_messages = VoiceMessageDetailSerializer(many=True, read_only=True)
    score_record = SimpleVoiceChatScoreSerializer(read_only=True)

    class Meta:
        model = VoiceChat
        fields = [
            "id",
            "character",
            "scenario",
            "gradient_start_color",
            "gradient_end_color",
            "started_at",
            "completed_at",
            "score_record",
            "voice_messages",
        ]
        read_only_fields = [
            "id",
            "gradient_start_color",
            "gradient_end_color",
            "started_at",
            "completed_at"
        ]


class VoiceChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceChat
        fields = ["scenario"]
