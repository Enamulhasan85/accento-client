from rest_framework import serializers

from bold_voice.conversations.api.v1.serializers.character import CharacterSerializer
from bold_voice.conversations.models import Scenario, Category


class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'title',
            'type'
        ]


class ScenarioSerializer(serializers.ModelSerializer):
    category = SimpleCategorySerializer(read_only=True)
    character = CharacterSerializer(read_only=True)

    class Meta:
        model = Scenario
        fields = [
            'id',
            'title',
            'subtitle',
            'description',
            'category',
            'character',
            'character_role',
            'sort_order',
            'icon',
            'gradient_start_color',
            'gradient_end_color',
            'is_premium',
        ]
