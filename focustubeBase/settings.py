
from decouple import config  # Import config from decouple this is used to load environment variables

from pathlib import Path
import os
import dj_database_url
# from decouple import Config, RepositoryEnv


from environ import Env





# from dotenv import load_dotenv
# load_dotenv()  # Load environment variables from .env


# # Access your key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

DEEPSEEK_API_KEY = os.getenv("api_key_deepseek")
# DEEPSEEK_API_KEY = config("api_key_deepseek", default=None)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
# SECRET_KEY = 'django-insecure-ix0fhowl+*n@nfmn=$bn_&cpq3vteo@_jh_bk*j#jtuk^fudgq'
# Initialize environment variables
# Initialize environment
env = Env()
Env.read_env(os.path.join(BASE_DIR, '.env'))  # Load .env from BASE_DIR

# Get environment mode, default to 'development'
SECRET_KEY = env('SECRET_KEY')


# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == "development":
    DEBUG = False
else:
    DEBUG = False
# settings.py
# REST_FRAMEWORK = {
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 10,  # adjust as needed
# }

ALLOWED_HOSTS = ['*']

# Application definition for the API
# APPEND_SLASH = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

     'rest_framework',
    'corsheaders',
    'api',
    'rest_framework_simplejwt',
    # 'admin_honeypot',

]

MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',


]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    # "http://localhost:3000",
    # "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    # "http://localhost:3000",  # ✅ include the scheme (http/https)
]

CSRF_TRUSTED_ORIGINS = [
    # "https://focustube.online",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

ROOT_URLCONF = 'focustubeBase.urls'

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

WSGI_APPLICATION = 'focustubeBase.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# import dj_database_url
# from decouple import config as env
ENVIRONMENT = env('ENVIRONMENT', default='development')

# Configure database depending on environment
if ENVIRONMENT == 'production':
    DATABASES = {
        'default': dj_database_url.parse(env('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# USERNAME_BLACKLIST = [
#     'admin', 'root', 'support', 'staff', 'superuser',
#     'moderator', 'help', 'null', 'none', 'me', 'system','abuu_luquman',
# ]
