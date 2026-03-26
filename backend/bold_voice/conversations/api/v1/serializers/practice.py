from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class PracticeSpeakingTextSerializer(serializers.Serializer):
    text = serializers.CharField(help_text="The practice text content")
    audio = serializers.FileField(help_text="The practice audio file matching the text content")


class PracticeSpeakingTextResponseSerializer(serializers.Serializer):
    score = serializers.FloatField(help_text="The score of the practice")
    word_scores = serializers.SerializerMethodField(
        help_text="List of word scores with their status and timing information"
    )

    @extend_schema_field({
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "word": {"type": "string", "example": "Word"},
                "status": {
                    "type": "string",
                    "enum": ["matched", "mismatch", "missing"],
                    "example": "matched"
                },
                "score": {"type": "number", "format": "float", "example": 0.764},
                "start": {"type": "number", "format": "float", "example": 4.88},
                "end": {"type": "number", "format": "float", "example": 5.12}
            },
            "required": ["word", "status"]
        }
    })
    def get_word_scores(self, obj):
        return obj.get('word_scores', [])
