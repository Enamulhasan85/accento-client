from rest_framework import serializers

from bold_voice.conversations.models import PracticeTextBookmark


class PracticeTextBookmarkSerializer(serializers.ModelSerializer):
    """Serializer for PracticeTextBookmark model."""

    class Meta:
        model = PracticeTextBookmark
        fields = ['id', 'practice_text', 'score', 'word_scores', 'attempt_count']
        read_only_fields = ['attempt_count']
