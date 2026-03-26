import django_filters

from bold_voice.conversations.models import VoiceChat


class VoiceChatFilter(django_filters.FilterSet):
    scenario = django_filters.NumberFilter(field_name='scenario__id', lookup_expr='exact')

    class Meta:
        model = VoiceChat
        fields = ['scenario']
