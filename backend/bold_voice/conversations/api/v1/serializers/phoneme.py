from rest_framework import serializers

from bold_voice.conversations.models import PhonemeCategory, Phoneme, PhonemeExample


class PhonemeExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhonemeExample
        fields = [
            'id',
            'word',
            'marks',
            'audio_file',
            'sort_order',
        ]


class PhonemeListSerializer(serializers.ModelSerializer):
    examples = PhonemeExampleSerializer(many=True, read_only=True)

    class Meta:
        model = Phoneme
        fields = [
            'id',
            'symbol',
            'phonetic',
            'tip',
            'audio_file',
            'card_color',
            'sort_order',
            'examples',
        ]


class PhonemeCategorySerializer(serializers.ModelSerializer):
    phonemes = PhonemeListSerializer(many=True, read_only=True)

    class Meta:
        model = PhonemeCategory
        fields = [
            'id',
            'title',
            'sort_order',
            'phoneme_type',
            'phonemes'
        ]


class PhonemeDetailSerializer(serializers.ModelSerializer):
    examples = PhonemeExampleSerializer(many=True, read_only=True)
    confused_phonemes = PhonemeListSerializer(many=True, read_only=True)

    class Meta:
        model = Phoneme
        fields = [
            'id',
            'symbol',
            'phonetic',
            'tip',
            'audio_file',
            'card_color',
            'sort_order',
            'examples',
            'confused_phonemes',
        ]
