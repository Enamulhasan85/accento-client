from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bold_voice.conversations'

    def ready(self):
        import bold_voice.conversations.signals  # noqa: F401
