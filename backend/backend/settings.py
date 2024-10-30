"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

from environs import Env



env = Env()
env.read_env()  # read .env file, if it exists
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

BACKEND_DOMAIN = env.str('BACKEND_DOMAIN', default='')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-trgynxv69d^o5u0!-qzaeqv*!0ual(-#6b_ey$_4#1g!e28zct'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)
BACKEND_DOMAIN_WITHOUT_PROTOCOL_WITHOUT_PORT = BACKEND_DOMAIN.split('//')[-1].split(':')[0]
ALLOWED_HOSTS = [BACKEND_DOMAIN_WITHOUT_PROTOCOL_WITHOUT_PORT,]
CSRF_TRUSTED_ORIGINS = [BACKEND_DOMAIN,]

# Application definition

INSTALLED_APPS = [
    "django_admin_index",
    "ordered_model",
    
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    
    'debug_toolbar',
    'storages',
    'adminsortable2',
    'import_export',
    
    'core',
    'models',
    'admin_dashboard',
    'counting',
    'dashboard',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'core.middleware.BreadcrumbsMiddleware',
    'core.middleware.NonHtmlDebugToolbarMiddleware',

]


if DEBUG is False:
    # MIDDLEWARE = MIDDLEWARE[1:]  # remove the first element of the list, which is the NonHtmlDebugToolbarMiddleware
    del MIDDLEWARE[0]


ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASE_TYPE = env.str('DATABASE_TYPE')
DATABASE_NAME = env.str('DATABASE_NAME', default='')
DATABASE_USER = env.str('DATABASE_USER', default='')
DATABASE_PASSWORD = env.str('DATABASE_PASSWORD', default='')
DATABASE_HOST = env.str('DATABASE_HOST', default='')
DATABASE_PORT = env.str('DATABASE_PORT', default='')

if DATABASE_TYPE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DATABASE_NAME,
            'USER': DATABASE_USER,
            'PASSWORD': DATABASE_PASSWORD,
            'HOST': DATABASE_HOST,
            'PORT': DATABASE_PORT,
        }
    }
elif DATABASE_TYPE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'he'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



USE_I18N = True

USE_L10N = True

# use timezone

TIME_ZONE = 'Israel'
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

# when changed, change allso templates location
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static_cdn"),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(STATIC_ROOT, 'media_root/')


LOGIN_REDIRECT_URL = '/admin-dashboard/messages/'
LOGIN_URL = '/admin/login/'
LOGOUT_REDIRECT_URL = '/admin/login/?next=' + LOGIN_REDIRECT_URL


# AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')

# AWS_STORAGE_BUCKET_NAME = 'django-development-bucket'
# # AWS_S3_SIGNATURE_NAME = None
# AWS_QUERYSTRING_AUTH = False
# AWS_S3_REGION_NAME = 'us-east-2'
# AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL =  None
# AWS_S3_VERITY = True
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]