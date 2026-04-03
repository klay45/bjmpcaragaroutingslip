"""
Django settings for epccid project (Render + Supabase deployment)
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url
from decouple import Config, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent.parent
'''
# -----------------------------
# Bulletproof .env reader
# -----------------------------
env_file = BASE_DIR / '.env'
env_vars = {}

if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()

# -----------------------------
# Load variables
# -----------------------------
SECRET_KEY = env_vars.get('SECRET_KEY')
DEBUG = env_vars.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
ALLOWED_HOSTS = env_vars.get('ALLOWED_HOSTS', '').split(',')
DATABASE_URL = env_vars.get('DATABASE_URL')

# -----------------------------
# Safety check
# -----------------------------
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in .env file!")'''
#new config
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set!")

#DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
DEBUG = True
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost','bjmpcaragaroutingslip.onrender.com').split(',')
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}
#until this
# -----------------------------
# APPLICATIONS
# -----------------------------
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'webid.apps.WebidConfig',
    'django_extensions',
    'sslserver',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files on Render
]

ROOT_URLCONF = 'epccid.urls'

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

# -----------------------------
# WSGI / ASGI
# -----------------------------
WSGI_APPLICATION = 'epccid.wsgi.application'
ASGI_APPLICATION = 'epccid.asgi.application'

# -----------------------------
# DATABASE
# -----------------------------
DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL'))
}

# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# -----------------------------
# STATIC FILES (CSS, JS)
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Where collectstatic will put files
STATICFILES_DIRS = [BASE_DIR / 'static']  # Optional local dev static
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -----------------------------
# MEDIA FILES (user uploads) - ignored for deployment
# -----------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Can be empty, won't push 25GB folder

# -----------------------------
# OTHER SETTINGS
# -----------------------------
IMPORT_EXPORT_USE_TRANSACTIONS = True
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
