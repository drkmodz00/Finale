"""
Django settings for morado_project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

import cloudinary
import cloudinary.uploader
import cloudinary.api

# ──────────────────────────────────────────────
# BASE DIRECTORY
# ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# load env FIRST
# load_dotenv(BASE_DIR / ".env")

if os.path.exists(BASE_DIR / ".env"):
    load_dotenv(BASE_DIR / ".env")

# ──────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY is missing")

DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".railway.app"]

# APPLICATIONS
# ──────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',
    'dmep',
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
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'
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

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}