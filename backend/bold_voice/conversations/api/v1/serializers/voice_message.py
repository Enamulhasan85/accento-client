from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from bold_voice.conversations.models import VoiceMessage, VoiceMessageScore


class SimpleVoiceMessageScoreSerializer(serializers.ModelSerializer):
    words = serializers.SerializerMethodField()

    class Meta:
        model = VoiceMessageScore
        fields = ["id", "score", "words", "suggested_words"]

    @extend_schema_field({
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "word": {"type": "string", "example": "string"},
                "start": {"type": "number", "format": "float", "example": 0},
                "end": {"type": "number", "format": "float", "example": 0},
                "score": {"type": "number", "format": "float", "example": 0}
            }
        },
        "example": [
            {"word": "string", "start": 0, "end": 0, "score": 0},
            {"word": "string", "start": 0, "end": 0, "score": 0}
        ]
    })
    def get_words(self, obj):
        return obj.words


class VoiceMessageDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed response of an audio message."""
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    score_record = SimpleVoiceMessageScoreSerializer(read_only=True)

    class Meta:
        model = VoiceMessage
        fields = [
            "id",
            "role",
            "role_display",
            "audio_file",
            "transcript",
            "created_at",
            "score_record",
        ]
        read_only_fields = ["id", "transcript", "score_record"]


class VoiceMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an audio message."""

    class Meta:
        model = VoiceMessage
        fields = ["role", "audio_file"]
        extra_kwargs = {
            "audio_file": {"required": False, "allow_null": True}
        }

    def validate(self, data):
        """
        Ensure that:
        - User messages require an audio file.
        - System/Assistant messages should not have an audio file.
        """
        role = data.get("role", VoiceMessage.Role.USER)
        audio_file = data.get("audio_file")

        if role == VoiceMessage.Role.USER and not audio_file:
            raise serializers.ValidationError(_("User messages must include an audio file."))

        if role == VoiceMessage.Role.ASSISTANT and audio_file:
            raise serializers.ValidationError(_("Assistant messages should not include an audio file."))

        return data


class VoiceMessagePracticeWordSerializer(serializers.Serializer):
    audio_file = serializers.FileField(
        required=True,
        help_text="Audio file containing the user's pronunciation of the suggested word."
    )
    voice_message_score = serializers.PrimaryKeyRelatedField(
        queryset=VoiceMessageScore.objects.all(),
        required=True,
        help_text="The voice message score related to the suggested word."
    )
    suggested_word_index = serializers.IntegerField(
        required=True,
        min_value=0,
        help_text="Index of the suggested word within the suggested words list."
    )

    def validate(self, attrs):
        voice_message_score = attrs.get('voice_message_score')
        user = self.context['request'].user

        user_id = (
            VoiceMessageScore.objects.filter(pk=voice_message_score.pk)
            .values_list('voice_message__voice_chat__user_id', flat=True)
            .first()
        )

        if user_id != user.id:
            raise serializers.ValidationError(_("No voice message score found."))

        suggested_words = voice_message_score.suggested_words
        suggested_word_index = attrs.get('suggested_word_index')

        if suggested_word_index >= len(suggested_words):
            raise serializers.ValidationError(_("Suggested word index out of range."))

        return attrs
