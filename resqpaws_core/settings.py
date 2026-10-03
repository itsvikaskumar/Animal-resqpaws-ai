import os
from pathlib import Path
from dotenv import load_dotenv


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# LOAD .ENV FILE
# =========================================================

load_dotenv(BASE_DIR / '.env')


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'resqpaws-secret-key-mca-project-key-change-in-prod'
)

DEBUG = True

ALLOWED_HOSTS = ['*']


# =========================================================
# INSTALLED APPS
# (Daphne MUST be the very first entry for WebSockets)
# =========================================================

INSTALLED_APPS = [
    'daphne',  # REQUIRED: Must be at the top to enable ASGI & WebSockets

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
    'rescue_app',
]


# =========================================================
# ASGI & WSGI CONFIGURATION
# =========================================================

ROOT_URLCONF = 'resqpaws_core.urls'
WSGI_APPLICATION = 'resqpaws_core.wsgi.application'
ASGI_APPLICATION = 'resqpaws_core.asgi.application'


# =========================================================
# CHANNEL LAYERS (Required for Real-time WebSockets)
# =========================================================

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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


# =========================================================
# DATABASE
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
]


# =========================================================
# LANGUAGE & TIMEZONE
# =========================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# =========================================================
# MEDIA FILES
# =========================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================================================
# EMAIL SETTINGS
# =========================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv(
    'EMAIL_HOST_USER',
    'resqpaws.emergency@gmail.com'
)

EMAIL_HOST_PASSWORD = os.getenv(
    'EMAIL_HOST_PASSWORD',
    ''
)


# =========================================================
# GOOGLE GEMINI API
# =========================================================

GEMINI_API_KEY = os.getenv(
    'GEMINI_API_KEY',
    ''
)