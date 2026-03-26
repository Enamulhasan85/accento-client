from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from bold_voice.conversations.models import SpeechScanSession, SpeechScanConfig, SpeechScanSessionScoreDetail


class SpeechScanConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechScanConfig
        fields = [
            'id',
            'title',
            'description',
            'practice_texts',
        ]


class SpeechScanSessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechScanSession
        fields = [
            'id',
            'overall_score',
            'created_at',
        ]
        read_only_fields = ['overall_score', 'created_at']


class SpeechScanSessionScoreDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechScanSessionScoreDetail
        fields = [
            'practice_text_index',
            'score',
            'word_scores',
            'audio_file',
        ]


class SpeechScanSessionDetailSerializer(serializers.ModelSerializer):
    speech_scan_config = SpeechScanConfigSerializer(read_only=True)
    score_details = SpeechScanSessionScoreDetailSerializer(many=True, read_only=True)

    class Meta:
        model = SpeechScanSession
        fields = [
            'id',
            'speech_scan_config',
            'overall_score',
            'suggested_words',
            'strong_words',
            'created_at',
            'score_details',
        ]
        read_only_fields = ['speech_scan_config', 'created_at', ]


class SpeechScanSessionPracticeTextSerializer(serializers.Serializer):
    audio_file = serializers.FileField(required=True, help_text="Audio file for the practice text.")
    practice_text_index = serializers.IntegerField(
        required=True,
        help_text="Index of the practice text in the session's practice texts."
    )

    def validate(self, attrs):
        speech_scan_session = self.context.get('speech_scan_session')
        user = self.context['request'].user

        if speech_scan_session.user != user:
            raise serializers.ValidationError(_("You do not have permission to add practice texts to this session."))

        practice_text_index = attrs.get('practice_text_index')
        if (practice_text_index < 0 or
                practice_text_index >= len(speech_scan_session.speech_scan_config.practice_texts)):
            raise serializers.ValidationError(_("Practice text index invalid."))

        return attrs
