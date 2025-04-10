import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

## ENV SETTINGS
# Load environment variables
load_dotenv()
# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent
# Security settings
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'False'
# WSGI application
WSGI_APPLICATION = 'metaapi.wsgi.application'


## SECURITY 
#ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'metaapi.up.railway.app']
CSRF_TRUSTED_ORIGINS = [
'https://*.railway.app'
]
# Password validation settings
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
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]


## INSTALLED APPS 
# Installed applications
INSTALLED_APPS = [
    # admin page theme (url: https://unfoldadmin.com/docs/)
    "unfold",                           # unfold admin package
    "unfold.contrib.filters",  
    "unfold.contrib.forms", 
    "unfold.contrib.inlines",  
    "unfold.contrib.import_export",  
    "unfold.contrib.simple_history", 

    # django-related packages 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # installed apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_yasg',                         # generates documentation at /api/docs
    'djmoney',                          # to work w money and currencies

    # custom apps
    'catalog',
    'orders',
    'api',
    'accounting',
]
# Middleware settings
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# Redis cache configuration
CACHES = {
    "default": {
        # Specify django-redis as the cache backend
        "BACKEND": "django_redis.cache.RedisCache",
        
        # Get Redis URL from environment variables, with a fallback for local development
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        
        "OPTIONS": {
            # DefaultClient handles connection pooling and other Redis features
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            
            # HiredisParser is a C-based parser that's much faster than the Python parser
            "PARSER_CLASS": "redis.connection._HiredisParser",
            
            # Optional: Set a connection timeout (in seconds)
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            
            # Optional: Enable connection pooling with maximum connections
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            
            # Optional: For secure connections (if your Railway Redis uses SSL)
            # "SSL": True,
        }
    }
}

# Optional but recommended: Use Redis for sessions too
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

## DJANGO SETTINGS
APPEND_SLASH = False
LOGOUT_REDIRECT_URL = '/'
# Default auto field for models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# URL configuration
ROOT_URLCONF = 'metaapi.urls'
# Internationalization settings
LANGUAGE_CODE = 'uk'
LANGUAGES = [
    ('en', _('English')),
    ('uk', _('Ukrainian')),
    # add other languages if necessary
]
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
CURRENCIES = ('USD', 'UAH', 'EUR')
# Static files settings
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# Media files settings
MEDIA_ROOT = '/app/media'
MEDIA_URL = '/media/'
# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

## INSTALLED PACKAGES SETTINGS
# Unfold settings
UNFOLD = {
    "SITE_TITLE": "MetaPrint Admin",
    "SITE_HEADER": "MetaPrint",
    "SITE_SUBHEADER": "Administration",
    "SITE_URL": "/",
    "SITE_SYMBOL": "m",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True, 
    "COLORS": {
  "base": {
    "50": "249 250 251",
    "100": "243 244 246",
    "200": "229 231 235",
    "300": "209 213 219",
    "400": "156 163 175",
    "500": "107 114 128",
    "600": "75 85 99",
    "700": "55 65 81",
    "800": "31 41 55",
    "900": "17 24 39",
    "950": "3 7 18"
  },
  "primary": {
    "50": "240 253 250",
    "100": "204 251 241",
    "200": "153 246 228",
    "300": "94 234 212",
    "400": "45 212 191",
    "500": "20 184 166",
    "600": "13 148 136",
    "700": "15 118 110",
    "800": "17 94 89",
    "900": "19 78 74",
    "950": "4 47 46"
  },
  "font": {
    "subtle-light": "var(--color-base-500)",
    "subtle-dark": "var(--color-base-400)",
    "default-light": "var(--color-base-600)",
    "default-dark": "var(--color-base-300)",
    "important-light": "var(--color-base-900)",
    "important-dark": "var(--color-base-100)"
  },
  
}

}


# REST framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}
# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'LOGIN_URL': '/accounts/login/',
    'LOGOUT_URL': '/accounts/logout/',
}

## DATABASE SETTINGS
# Database settings
POSTGRES_LOCALLY = True
if POSTGRES_LOCALLY:
    DATABASES = {
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
    }





