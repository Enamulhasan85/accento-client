from django.apps import AppConfig


class IdentityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bold_voice.identity'

    def ready(self):
        import bold_voice.identity.signals  # noqa: F401
