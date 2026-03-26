from django.contrib import admin
from django.utils.html import format_html

from bold_voice.common.admin import TimestampModelAdmin
from bold_voice.conversations.models import (
    Character,
    VoiceChat,
    VoiceMessage,
    Category,
    Scenario,
    VoiceChatScore,
    VoiceMessageScore,
    PhonemeCategory,
    Phoneme,
    PhonemeExample,
    PracticeTextBookmark, SpeechScanConfig, SpeechScanSession
)


@admin.register(Character)
class CharacterAdmin(TimestampModelAdmin):
    list_display = ("name", "voice_type", "image_preview",)
    search_fields = ("name",)
    ordering = ("name",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(TimestampModelAdmin):
    list_display = ("title", "type", "sort_order")
    list_filter = ("type",)
    search_fields = ("title",)
    ordering = ("type", "sort_order",)


@admin.register(Scenario)
class ScenarioAdmin(TimestampModelAdmin):
    list_display = ("title", "category", "character", "is_premium", "sort_order")
    list_filter = ("category", "is_premium")
    search_fields = ("title", "character__name", "category__title")
    ordering = ("category__sort_order", "sort_order")
    autocomplete_fields = ("category", "character")


@admin.register(VoiceChat)
class VoiceChatAdmin(TimestampModelAdmin):
    list_display = ("id", "user", "character", "scenario", "started_at", "completed_at")
    list_filter = ("character", "scenario", "started_at", "completed_at")
    search_fields = ("user__username", "character__name", "scenario__title")
    ordering = ("-id",)
    date_hierarchy = "started_at"
    readonly_fields = ("started_at",)
    autocomplete_fields = ("user",)


@admin.register(VoiceChatScore)
class VoiceChatScoreAdmin(TimestampModelAdmin):
    list_display = ("voice_chat", "ai_score", "num_words_spoken", "num_perfect_words", "time_spoken")
    search_fields = ("voice_chat__id",)
    ordering = ("-id",)


@admin.register(VoiceMessage)
class VoiceMessageAdmin(TimestampModelAdmin):
    list_display = ("id", "voice_chat", "role", "transcript", "audio_file")
    list_filter = ("role", "voice_chat")
    search_fields = ("transcript", "voice_chat__user__username")
    ordering = ("-id",)
    readonly_fields = ("created_at",)


@admin.register(VoiceMessageScore)
class VoiceMessageScoreAdmin(TimestampModelAdmin):
    list_display = ("voice_message", "score")
    search_fields = ("voice_message__id",)
    ordering = ("-id",)


@admin.register(PhonemeCategory)
class PhonemeCategoryAdmin(TimestampModelAdmin):
    list_display = ("title", "phoneme_type", "sort_order")
    list_filter = ("phoneme_type",)
    search_fields = ("title",)
    ordering = ("phoneme_type", "sort_order")


@admin.register(Phoneme)
class PhonemeAdmin(TimestampModelAdmin):
    list_display = ("symbol", "phonetic", "category", "card_color", "sort_order")
    list_filter = ("category",)
    search_fields = ("symbol", "phonetic", "category__title")
    ordering = ("category__sort_order", "sort_order")
    autocomplete_fields = ("category",)


@admin.register(PhonemeExample)
class PhonemeExampleAdmin(TimestampModelAdmin):
    list_display = ("phoneme", "word", "marks", "audio_file")
    list_filter = ("phoneme",)
    search_fields = ("word", "phoneme__symbol")
    ordering = ("phoneme__sort_order", "sort_order",)
    autocomplete_fields = ("phoneme",)


@admin.register(PracticeTextBookmark)
class PracticeTextBookmarkAdmin(TimestampModelAdmin):
    list_display = ("user", "practice_text", "score", "created_at")
    search_fields = ("user__username", "practice_text")
    ordering = ("-created_at",)
    autocomplete_fields = ("user",)


@admin.register(SpeechScanConfig)
class SpeechScanConfigAdmin(TimestampModelAdmin):
    list_display = ("title", "description", "is_active", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(SpeechScanSession)
class SpeechScanSessionAdmin(TimestampModelAdmin):
    list_display = ("user", "speech_scan_config", "overall_score", "created_at")
    search_fields = ("user__username", "speech_scan_config__title")
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "speech_scan_config")
