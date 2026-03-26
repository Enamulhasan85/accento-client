from .base import *  # noqa: F401

# https://docs.djangoproject.com/en/dev/ref/settings/
DEBUG = env.bool('DJANGO_DEBUG', True)
SECRET_KEY = env('DJANGO_SECRET_KEY', default='my-secret-key')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '0.0.0.0', '127.0.0.1'])

# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
        # Disable profiling panel due to an issue with Python 3.12:
        # https://github.com/jazzband/django-debug-toolbar/issues/1875
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

INTERNAL_IPS = env.list('INTERNAL_IPS', default=['localhost', '127.0.0.1'])

# https://docs.celeryq.dev/en/stable/userguide/configuration.html
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# For development, emails will be printed to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
