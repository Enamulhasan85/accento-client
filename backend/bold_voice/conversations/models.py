from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from bold_voice.common.models import TimestampModel


class Character(TimestampModel):
    """Model for fixed characters/personas that speak in the voice chats."""

    class VoiceType(models.TextChoices):
        MALE = "male", _("male")
        FEMALE = "female", _("female")

    name = models.CharField(
        verbose_name=_("character name"),
        max_length=100,
        unique=True
    )
    description = models.TextField(
        verbose_name=_("character description"),
        help_text=_("description of the character/persona")
    )
    voice_type = models.CharField(
        verbose_name=_("voice type"),
        max_length=50,
        choices=VoiceType.choices,
        default=VoiceType.MALE
    )
    image = models.ImageField(
        verbose_name=_("character image"),
        upload_to="character_images/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name}: {self.voice_type}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("character")
        verbose_name_plural = _("characters")


class Category(TimestampModel):
    """Model representing a category for scenarios."""

    class Type(models.TextChoices):
        ROLEPLAY = "roleplay", _("roleplay")
        TOPIC = "topic", _("topic")

    title = models.CharField(
        verbose_name=_("title"),
        max_length=255
    )
    sort_order = models.IntegerField(
        verbose_name=_("sort order"),
        default=0
    )
    type = models.CharField(
        verbose_name=_("type"),
        max_length=10,
        choices=Type.choices
    )

    def __str__(self):
        return self.title

    class Meta(TimestampModel.Meta):
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class Scenario(TimestampModel):
    """Model representing a conversation scenario (roleplay or topic)."""

    title = models.CharField(
        verbose_name=_("title"),
        max_length=255
    )
    subtitle = models.CharField(
        verbose_name=_("subtitle"),
        max_length=255
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True,
        null=True,
        help_text=_(
            "Description of the scenario. Used to provide context or instructions for the conversation in the prompt."
        )
    )
    initial_texts = models.JSONField(
        verbose_name=_("initial text"),
        default=list,
        blank=True,
        help_text=_("Initial texts to start the conversation, stored as a list of strings")
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        on_delete=models.PROTECT,
        related_name="scenarios"
    )
    character = models.ForeignKey(
        Character,
        verbose_name=_("character"),
        on_delete=models.PROTECT,
        related_name="scenarios"
    )
    character_role = models.CharField(
        verbose_name=_("character role"),
        max_length=255,
        help_text=_("the role this character plays in the scenario")
    )
    sort_order = models.IntegerField(
        verbose_name=_("sort order"),
        default=0
    )
    icon = models.ImageField(
        verbose_name=_("icon"),
        upload_to="scenario_icons/",
        blank=True,
        null=True
    )
    gradient_start_color = models.CharField(
        verbose_name=_("gradient start color"),
        max_length=7,
        help_text=_("hex code of the gradient start color")
    )
    gradient_end_color = models.CharField(
        verbose_name=_("gradient end color"),
        max_length=7,
        help_text=_("hex code of the gradient end color")
    )
    is_premium = models.BooleanField(
        verbose_name=_("is premium"),
        default=False
    )

    def __str__(self):
        return f"{self.title}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("scenario")
        verbose_name_plural = _("scenarios")


class VoiceChat(TimestampModel):
    """Model representing a voice chat session."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="voice_chats"
    )
    character = models.ForeignKey(
        Character,
        verbose_name=_("character"),
        on_delete=models.PROTECT,
        related_name="voice_chats"
    )
    scenario = models.ForeignKey(
        Scenario,
        verbose_name=_("scenario"),
        on_delete=models.PROTECT,
        related_name="voice_chats"
    )
    gradient_start_color = models.CharField(
        verbose_name=_("gradient start color"),
        max_length=7,
        help_text=_("hex code of the gradient start color")
    )
    gradient_end_color = models.CharField(
        verbose_name=_("gradient end color"),
        max_length=7,
        help_text=_("hex code of the gradient end color")
    )
    started_at = models.DateTimeField(
        verbose_name=_("start time"),
        auto_now_add=True
    )
    completed_at = models.DateTimeField(
        verbose_name=_("completion time"),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"VoiceChat {self.id} - ({self.scenario})"

    class Meta(TimestampModel.Meta):
        verbose_name = _("voice chat")
        verbose_name_plural = _("voice chats")


class VoiceChatScore(TimestampModel):
    """Model for storing scores and feedback for voice chats."""

    voice_chat = models.OneToOneField(
        VoiceChat,
        verbose_name=_("voice chat"),
        on_delete=models.CASCADE,
        related_name="score_record"
    )
    ai_score = models.FloatField(
        verbose_name=_("ai score"),
        default=0
    )
    total_word_score = models.FloatField(
        verbose_name=_("total word score"),
        default=0
    )
    num_words_spoken = models.IntegerField(
        verbose_name=_("total words spoken"),
        default=0
    )
    num_perfect_words = models.IntegerField(
        verbose_name=_("total correctly pronounced words"),
        default=0
    )
    time_spoken = models.FloatField(
        verbose_name=_("duration in seconds"),
        default=0.0
    )
    feedback = models.TextField(
        verbose_name=_("feedback"),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Score {self.ai_score} for VoiceChat {self.voice_chat_id}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("voice chat score")
        verbose_name_plural = _("voice chat scores")


def audio_upload_path(instance, filename):
    """Dynamically generate the relative audio file path."""
    return f"voice_chats/user_{instance.voice_chat.user.id}/chat_{instance.voice_chat.id}/{filename}"


class VoiceMessage(TimestampModel):
    """Model representing a voice message in a voice chat."""

    class Role(models.TextChoices):
        SYSTEM = "system", _("system")
        ASSISTANT = "assistant", _("assistant")
        USER = "user", _("user")

    voice_chat = models.ForeignKey(
        VoiceChat,
        verbose_name=_("voice chat"),
        on_delete=models.CASCADE,
        related_name="voice_messages"
    )
    role = models.CharField(
        verbose_name=_("message role"),
        max_length=10,
        choices=Role.choices
    )
    audio_file = models.FileField(
        verbose_name=_("audio file"),
        upload_to=audio_upload_path
    )
    transcript = models.TextField(
        verbose_name=_("transcript"),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Message in {self.voice_chat_id} by {self.get_role_display()}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("voice message")
        verbose_name_plural = _("voice messages")


class VoiceMessageScore(TimestampModel):
    """Model for storing scores related to a voice message."""

    voice_message = models.OneToOneField(
        VoiceMessage,
        verbose_name=_("voice message"),
        on_delete=models.CASCADE,
        related_name="score_record"
    )
    score = models.FloatField(
        verbose_name=_("score"),
        default=0
    )
    words = models.JSONField(
        verbose_name=_("words"),
        default=list,
        blank=True
    )
    suggested_words = models.JSONField(
        verbose_name=_("suggested words"),
        default=list,
        blank=True
    )

    def __str__(self):
        return f"Score for message {self.voice_message_id}: {self.score}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("voice message score")
        verbose_name_plural = _("voice message scores")


class PhonemeCategory(TimestampModel):
    """Model representing a category of phonemes."""

    class PhonemeType(models.TextChoices):
        VOWEL = "vowel", _("vowel")
        CONSONANT = "consonant", _("consonant")

    title = models.CharField(
        verbose_name=_("title"),
        max_length=255
    )
    sort_order = models.IntegerField(
        verbose_name=_("sort order"),
        default=0
    )
    phoneme_type = models.CharField(
        verbose_name=_("phoneme type"),
        max_length=10,
        choices=PhonemeType.choices
    )

    def __str__(self):
        return self.title

    class Meta(TimestampModel.Meta):
        verbose_name = _("phoneme category")
        verbose_name_plural = _("phoneme categories")


class Phoneme(TimestampModel):
    """Model representing a phoneme."""

    category = models.ForeignKey(
        PhonemeCategory,
        verbose_name=_("category"),
        on_delete=models.PROTECT,
        related_name="phonemes"
    )
    symbol = models.CharField(
        verbose_name=_("symbol"),
        max_length=25,
    )
    phonetic = models.CharField(
        verbose_name=_("phonetic"),
        max_length=255,
        blank=True,
        null=True
    )
    tip = models.TextField(
        verbose_name=_("tip"),
        blank=True,
        null=True
    )
    audio_file = models.FileField(
        verbose_name=_("audio file"),
        blank=True,
        null=True,
        upload_to="phonemes/"
    )
    card_color = models.CharField(
        verbose_name=_("card color"),
        max_length=7,
        help_text=_("hex code of the card color")
    )
    sort_order = models.IntegerField(
        verbose_name=_("sort order"),
        default=0
    )
    confused_phonemes = models.ManyToManyField(
        verbose_name=_("confused phonemes"),
        to="self",
        blank=True
    )

    def __str__(self):
        return f"{self.symbol} ({self.phonetic}) - {self.category.title}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("phoneme")
        verbose_name_plural = _("phonemes")


class PhonemeExample(TimestampModel):
    """Model representing an example for a phoneme."""

    phoneme = models.ForeignKey(
        Phoneme,
        verbose_name=_("phoneme"),
        on_delete=models.CASCADE,
        related_name="examples"
    )
    word = models.CharField(
        verbose_name=_("word"),
        max_length=255,
    )
    marks = models.JSONField(
        verbose_name=_("marks"),
        default=list,
        blank=True
    )
    audio_file = models.FileField(
        verbose_name=_("audio file"),
        blank=True,
        null=True,
        upload_to="phoneme_examples/"
    )
    sort_order = models.IntegerField(
        verbose_name=_("sort order"),
        default=0
    )

    def __str__(self):
        return f"Example for {self.phoneme.symbol}: {self.word}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("phoneme example")
        verbose_name_plural = _("phoneme examples")


class PracticeTextBookmark(TimestampModel):
    """Model representing a bookmark for practice text."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="practice_text_bookmarks"
    )
    practice_text = models.TextField(
        verbose_name=_("practice text"),
        help_text=_("the practice text content")
    )
    score = models.FloatField(
        verbose_name=_("score"),
        default=0.0,
        help_text=_("the score of the practice text")
    )
    word_scores = models.JSONField(
        verbose_name=_("word scores"),
        default=list,
        blank=True,
        help_text=_("list of word scores with their status and timing information")
    )
    attempt_count = models.IntegerField(
        verbose_name=_("attempt count"),
        default=0,
        help_text=_("the number of times this text has been practiced")
    )

    def __str__(self):
        return f"Bookmark by {self.user.username} for practice text"

    class Meta(TimestampModel.Meta):
        verbose_name = _("practice text bookmark")
        verbose_name_plural = _("practice text bookmarks")


class SpeechScanConfig(TimestampModel):
    """
    Model for storing configuration or setup for speech scan sessions.
    """
    title = models.CharField(
        verbose_name=_("title"),
        max_length=255,
        help_text=_("Configuration title or name")
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True,
        null=True,
        help_text=_("Description of the configuration")
    )
    practice_texts = models.JSONField(
        verbose_name=_("practice texts"),
        default=list,
        blank=True,
        help_text=_("List of texts to be used in speech scan sessions")
    )
    is_active = models.BooleanField(
        verbose_name=_("is active"),
        default=True,
        help_text=_("Whether this configuration is active")
    )

    def __str__(self):
        return self.title

    class Meta(TimestampModel.Meta):
        verbose_name = _("speech scan configuration")
        verbose_name_plural = _("speech scan configurations")


class SpeechScanSession(TimestampModel):
    """Model representing a speech scan for user to practice speaking."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="speech_scan_sessions"
    )
    speech_scan_config = models.ForeignKey(
        SpeechScanConfig,
        verbose_name=_("speech scan configuration"),
        on_delete=models.PROTECT,
        related_name="sessions"
    )
    overall_score = models.FloatField(
        verbose_name=_("overall score"),
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_("Average score across all practice texts in this session")
    )
    suggested_words = models.JSONField(
        verbose_name=_("suggested words"),
        default=list,
        blank=True,
        help_text=_("list of suggested words for the user to practice")
    )
    strong_words = models.JSONField(
        verbose_name=_("strong words"),
        default=list,
        blank=True,
        help_text=_("list of words the user pronounced well")
    )

    def update_scores_and_words(self):
        score_list = []
        suggested = set()
        strong = set()

        for detail in self.score_details.all():
            score = detail.score
            score_list.append(score)

            word_scores = detail.word_scores
            for word_score in word_scores:
                word = word_score.get('word').capitalize()
                word_score = word_score.get('score')

                if word_score < settings.WEAK_WORD_MAX_SCORE:
                    suggested.add(word)
                elif word_score >= settings.PERFECT_WORD_MIN_SCORE:
                    strong.add(word)

        self.overall_score = sum(score_list) / len(score_list) if score_list else 0.0
        self.suggested_words = list(suggested)
        self.strong_words = list(strong)

        self.save(update_fields=['overall_score', 'suggested_words', 'strong_words'])

    def __str__(self):
        return f"Speech Scan by {self.user.username}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("speech scan session")
        verbose_name_plural = _("speech scan sessions")


class SpeechScanSessionScoreDetail(TimestampModel):
    """Model for storing scores and details for each practice text in a speech scan session."""

    speech_scan_session = models.ForeignKey(
        SpeechScanSession,
        verbose_name=_("speech scan session"),
        on_delete=models.CASCADE,
        related_name="score_details"
    )
    practice_text_index = models.PositiveIntegerField(verbose_name=_("practice text index"))
    score = models.FloatField(
        verbose_name=_("score"),
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    word_scores = models.JSONField(
        verbose_name=_("word scores"),
        default=list,
        blank=True,
        help_text=_("list of word scores with their status and timing information")
    )
    audio_file = models.FileField(
        verbose_name=_("audio file"),
        blank=True,
        null=True,
        upload_to="speech_scan_audio/",
    )

    def __str__(self):
        return f"Score Detail for Session {self.speech_scan_session_id} - Text {self.practice_text_index}"

    class Meta(TimestampModel.Meta):
        verbose_name = _("speech scan session score detail")
        verbose_name_plural = _("speech scan session score details")
