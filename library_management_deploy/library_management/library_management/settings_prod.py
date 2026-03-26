from .settings import *
import os
from decouple import config, Csv
import dj_database_url

# SECURITY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-library-management-system-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

# WHITENOISE for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# STATIC FILES
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# DATABASE — use DATABASE_URL env var if set (for PostgreSQL on Railway/Render)
# Falls back to SQLite for local dev
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
