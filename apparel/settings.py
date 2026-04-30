"""
Django settings for morado_project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
import cloudinary
import cloudinary_storage

# ──────────────────────────────────────────────
# BASE DIRECTORY
# ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# load env FIRST
load_dotenv(BASE_DIR / ".env")

# ──────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-use-env-variable")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
# ──────────────────────────────────────────────
# APPLICATIONS
# ──────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'dmep',
    'cloudinary',
    'cloudinary_storage',
]

# ──────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}
# ──────────────────────────────────────────────
# URLS
# ──────────────────────────────────────────────

ROOT_URLCONF = 'apparel.urls'

# ──────────────────────────────────────────────
# TEMPLATES
# ──────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'dmep.context_processors.cart_count',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ──────────────────────────────────────────────
# WSGI
# ──────────────────────────────────────────────

WSGI_APPLICATION = 'apparel.wsgi.application'

# ──────────────────────────────────────────────
# DATABASE (FIXED - SUPABASE READY)
# ──────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL is missing")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL.strip(),
        conn_max_age=600,
    )
}
# ──────────────────────────────────────────────
# PASSWORD VALIDATION
# ──────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────────
# INTERNATIONALIZATION
# ──────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────
# STATIC FILES
# ──────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ──────────────────────────────────────────────
# MEDIA FILES
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ──────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ──────────────────────────────────────────────
# LOGIN SETTINGS
# ──────────────────────────────────────────────

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'