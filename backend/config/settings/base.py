"""Base settings to build other settings files upon."""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / 'bold_voice'
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

env = environ.Env()
env.read_env(str(BASE_DIR / '.env'))

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Third-party apps
    'corsheaders',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',
    'drf_spectacular',
    'phonenumber_field',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',

    # dj-rest-auth
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.apple',

    # Local apps
    'bold_voice.identity',
    'bold_voice.conversations',
]

# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    # Security middleware should always be first
    'django.middleware.security.SecurityMiddleware',
    # CORS headers need to be processed early, right after security
    'corsheaders.middleware.CorsMiddleware',
    # Session handling follows
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Common middleware for processing basic requests
    'django.middleware.common.CommonMiddleware',
    # CSRF protection
    'django.middleware.csrf.CsrfViewMiddleware',
    # Authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Messages framework
    'django.contrib.messages.middleware.MessageMiddleware',
    # Django allauth account handling
    'allauth.account.middleware.AccountMiddleware',
    # Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL'),
}

# https://docs.djangoproject.com/en/dev/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = [str(APPS_DIR / 'fixtures')]

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = 'identity.User'

# https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#specifying-authentication-backends
AUTHENTICATION_BACKENDS = [
    'bold_voice.identity.backends.UsernameOrEmailAuthBackend',
]

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# https://docs.djangoproject.com/en/dev/topics/i18n/
USE_TZ = True
TIME_ZONE = 'UTC'
USE_I18N = True
LANGUAGE_CODE = 'en-us'

# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'config.urls'

# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
STATIC_ROOT = str(BASE_DIR / 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [str(APPS_DIR / 'static')]

MEDIA_ROOT = str(APPS_DIR / 'media')
MEDIA_URL = '/media/'

# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR / 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'debug.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'stripe': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'stripe.log',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'stripe': {
            'handlers': ['stripe'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# https://docs.celeryq.dev/en/stable/userguide/configuration.html
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'bold_voice.common.api.pagination.StandardResultsSetPagination',
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
        'bold_voice.common.api.filters.DefaultOrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": True,
}

# https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r'^/api/.*$'
if env.bool('CORS_ALLOW_ALL_ORIGINS', default=False):
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # If not allowing all origins, use CORS_ALLOWED_ORIGINS
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    'TITLE': 'Demo Project API',
    'DESCRIPTION': 'API documentation for the Demo project.',
    'VERSION': '1.0.0',
    # 'SCHEMA_PATH_PREFIX': '/api/v[0-9]',
}

# https://dj-rest-auth.readthedocs.io/en/latest/installation.html
ACCOUNT_ADAPTER = 'bold_voice.identity.api.adapters.CustomAccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        },
    },
}

REST_AUTH = {
    'USER_DETAILS_SERIALIZER': 'bold_voice.identity.api.v1.serializers.users.UserSerializer',
    'SESSION_LOGIN': False,
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,
    'JWT_SERIALIZER': 'bold_voice.identity.api.v1.serializers.jwt.JWTSerializer',
}

FRONTEND_EMAIL_CONFIRMATION_URL = env('FRONTEND_EMAIL_CONFIRMATION_URL')
FRONTEND_PASSWORD_RESET_URL = env('FRONTEND_PASSWORD_RESET_URL')

AI_CHAT_HISTORY_LIMIT = env.int('AI_CHAT_HISTORY_LIMIT', default=8)
VOICECHAT_MESSAGE_LIMIT = env.int('VOICECHAT_MESSAGE_LIMIT', default=8)
PERFECT_WORD_MIN_SCORE = env.float('PERFECT_WORD_MIN_SCORE', default=0.9)
WEAK_WORD_MAX_SCORE = env.float('WEAK_WORD_MAX_SCORE', default=0.75)

OPENAI_API_KEY = env.str('OPENAI_API_KEY')
OPENAI_TRANSCRIPT_GENERATION_MODEL = env.str('OPENAI_TRANSCRIPT_GENERATION_MODEL', "gpt-4o-mini-2024-07-18")
DEEPGRAM_API_KEY = env.str('DEEPGRAM_API_KEY')
DEEPGRAM_AUDIO_ANALYSIS_MODEL = env.str('DEEPGRAM_AUDIO_ANALYSIS_MODEL', "nova-3")
