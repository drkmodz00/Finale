"""
Django settings for morado_project.
"""

from pathlib import Path
import os

# ──────────────────────────────────────────────
# BASE DIRECTORY
# ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent


# ──────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────

SECRET_KEY = 'django-insecure-change-this-in-production-use-env-variable'

DEBUG = True  # Set to False in production

ALLOWED_HOSTS = ['*']  # Restrict to your domain in production


# ──────────────────────────────────────────────
# APPLICATIONS
# ──────────────────────────────────────────────

INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'dmep',
]


# ──────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serves static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ──────────────────────────────────────────────
# URL CONFIGURATION
# ──────────────────────────────────────────────

ROOT_URLCONF = 'apparel.urls'


# ──────────────────────────────────────────────
# TEMPLATES
# ──────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',   # project-level templates folder
        ],
        'APP_DIRS': True,             # also loads from dmep/templates/
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
# DATABASE
# ──────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'dmep.db',
    }
}

# ── PostgreSQL (recommended for production) ──
# Uncomment and fill in to switch to PostgreSQL:
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'dmep_db'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }


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
TIME_ZONE = 'Asia/Manila'   # Philippine Standard Time
USE_I18N = True
USE_TZ = True


# ──────────────────────────────────────────────
# STATIC FILES
# ──────────────────────────────────────────────

# URL to access static files in the browser
STATIC_URL = '/static/'

# Where Django collects all static files when you run `collectstatic`
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional locations Django looks for static files (beyond app/static/ folders)
STATICFILES_DIRS = [
    BASE_DIR / 'static',   # project-level static folder
]

# WhiteNoise compression & caching (used in production)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ──────────────────────────────────────────────
# MEDIA FILES (user-uploaded files)
# ──────────────────────────────────────────────

# URL to access uploaded media in the browser
MEDIA_URL = '/media/'

# Where uploaded files are saved on disk
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ──────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ──────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ──────────────────────────────────────────────
# MESSAGES (flash messages framework)
# ──────────────────────────────────────────────

from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {
    message_constants.DEBUG:   'secondary',
    message_constants.INFO:    'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR:   'danger',
}


# ──────────────────────────────────────────────
# LOGIN / LOGOUT REDIRECTS
# ──────────────────────────────────────────────

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'