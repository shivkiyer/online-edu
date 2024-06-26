from pathlib import Path
from . import env as KEYS
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = KEYS.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Base URL
BASE_URL = KEYS.BASE_URL
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Django Rest Framework
    'rest_framework',
    # DRF Simple JWT
    'rest_framework_simplejwt',
    # custom apps'
    'user_auth',
    'courses',
    'registration',
    'lectures',
    'video_contents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

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

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom user
AUTH_USER_MODEL = 'user_auth.User'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=KEYS.ACCESS_TOKEN_TIME_LIMIT),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=KEYS.REFRESH_TOKEN_TIME_LIMIT)
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# Default language
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('de', _('German')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Where translations will be stored
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

MODELTRANSLATION_AUTO_POPULATE = True

# Account verification settings
# time limit in minutes
EMAIL_VERIFICATION_TIMELIMIT = KEYS.EMAIL_VERIFICATION_TIMELIMIT

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/test.log',
            'level': 'INFO',
            'formatter': 'regular'
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['file']
        }
    },
    'formatters': {
        'regular': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{'
        }
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files
MEDIA_ROOT = BASE_DIR / 'test_media'
MEDIA_URL = '/test-media/'
