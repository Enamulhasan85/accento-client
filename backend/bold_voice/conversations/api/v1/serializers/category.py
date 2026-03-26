from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from bold_voice.conversations.api.v1.serializers.character import CharacterSerializer
from bold_voice.conversations.models import Category, Scenario


class ScenarioInCategorySerializer(serializers.ModelSerializer):
    character = CharacterSerializer(read_only=True)
    has_practiced = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Scenario
        fields = [
            'id',
            'title',
            'subtitle',
            'description',
            'character',
            'character_role',
            'sort_order',
            'icon',
            'gradient_start_color',
            'gradient_end_color',
            'is_premium',
            'has_practiced',
            'completion_percentage'
        ]

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_has_practiced(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return bool(getattr(obj, 'user_voice_chats', []))
        return False

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_completion_percentage(self, obj):
        request = self.context.get('request', None)
        message_limit = self.context.get('message_limit')

        if request.user.is_authenticated and len(obj.user_voice_chats) > 0:
            message_count = float(obj.user_voice_chats[-1].message_count)
            divisor = float(message_limit)

            completion_percentage = round((message_count / divisor) * 100.0, 2)
            return completion_percentage

        return 0.0


class CategorySerializer(serializers.ModelSerializer):
    scenarios = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'title',
            'sort_order',
            'type',
            'scenarios'
        ]

    @extend_schema_field(ScenarioInCategorySerializer(many=True))
    def get_scenarios(self, obj):
        return ScenarioInCategorySerializer(
            obj.scenarios.all(),
            many=True,
            context=self.context
        ).data
