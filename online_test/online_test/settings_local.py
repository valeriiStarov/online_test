from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

SECRET_KEY = 'django-insecure-8sddnhx%5#t6hvcor!46%^zatkj(&dtrx%8k^zic@)6fddb$uu'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}