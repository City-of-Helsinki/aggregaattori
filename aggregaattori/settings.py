"""
Django settings for aggregaattori project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _
from environ import Env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, 'postgis://aggregaattori:aggregaattori@localhost/aggregaattori'),
    EMAIL_FROM_NAME=(str, "Aggregaattori"),
    EMAIL_FROM_ADDRESS=(str, "aggregaattori@example.com"),
    EMAIL_AUTH_NAME=(str, ''),
    EMAIL_AUTH_PASS=(str, ''),
    TUNNISTAMO_URL=(str, ''),
    TUNNISTAMO_USERNAME=(str, ''),
    TUNNISTAMO_PASSWORD=(str, ''),
)

env_filename = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_filename):
    env.read_env(env_filename)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Email settings
EMAIL_FROM_NAME = env('EMAIL_FROM_NAME')
EMAIL_FROM_ADDRESS = env('EMAIL_FROM_ADDRESS')

EMAIL_AUTH_NAME = env('EMAIL_AUTH_NAME')
EMAIL_AUTH_PASS = env('EMAIL_AUTH_PASS')

# User IDs are fetched from here
TUNNISTAMO_URL = env('TUNNISTAMO_URL')
TUNNISTAMO_USERNAME = env('TUNNISTAMO_USERNAME')
TUNNISTAMO_PASSWORD = env('TUNNISTAMO_PASSWORD')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework_gis',
    'rest_framework',
    'django_extensions',
    'parler',
    'modeltranslation',
    'django_filters',

    # For handling municipalities data, especially administrative divisions
    # that are used by the API to determine location.
    'munigeo',

    # Apps within this repository
    'stories'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aggregaattori.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'aggregaattori.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

default_database_url = env('DATABASE_URL')

DATABASES = {
    'default': env.db_url(
        default=default_database_url
    )
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Europe/Helsinki'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('fi', _('Finnish')),
    ('sv', _('Swedish')),
)

PARLER_LANGUAGES = {
    None: (
        {'code': 'en'},
        {'code': 'fi'},
        {'code': 'sv'},
    ),
    'default': {
        'fallback': 'en',
        'hide_untranslated': False,
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'stories.renderers.ActivityStreamsRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'stories.parsers.ActivityStreamsParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
}

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
local_settings_path = os.path.join(BASE_DIR, "local_settings.py")
if os.path.exists(local_settings_path):
    with open(local_settings_path) as fp:
        code = compile(fp.read(), local_settings_path, 'exec')
    exec(code, globals(), locals())


# If a secret key was not supplied from elsewhere, generate a random one
# and store it into a file called .django_secret.
if 'SECRET_KEY' not in locals():
    secret_file = os.path.join(BASE_DIR, '.django_secret')
    try:
        SECRET_KEY = open(secret_file).read().strip()
    except IOError:
        import random
        system_random = random.SystemRandom()
        try:
            SECRET_KEY = ''.join([system_random.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(64)]) # noqa
            secret = open(secret_file, 'w')
            os.chmod(secret_file, 0o0600)
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            Exception('Please create a %s file with random characters to generate your secret key!' % secret_file)
