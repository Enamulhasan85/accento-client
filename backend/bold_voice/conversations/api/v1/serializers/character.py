from rest_framework import serializers

from bold_voice.conversations.models import Character


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = [
            'id',
            'name',
            'description',
            'voice_type',
            'image',
        ]
