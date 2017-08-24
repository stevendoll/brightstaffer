"""
Django settings for brightStaffer project.

Generated by 'django-admin startproject' using Django 1.10.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import smtplib
from configparser import ConfigParser


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_NAME = 'brightstaffer.ini'
Config = ConfigParser()
config_file_path = os.path.join(BASE_DIR, 'brightStaffer', CONFIG_FILE_NAME)
Config.read(config_file_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o6!ny!e782=am=x*@pr$advkfnb5g!nd!%ag-1o86q&$7e*ua3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    #'material',
    #'material.admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'brightStafferapp',
    'rest_framework',
    'rest_framework.authtoken',
    'widget_tweaks',
    'haystack'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'brightStaffer.urls'

TEMPLATES = [

    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates", "brightStafferapp/static/"],
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

WSGI_APPLICATION = 'brightStaffer.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/how to/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = "media/"
MEDIA_URL = os.path.join(BASE_DIR, MEDIA_ROOT)
PDF_UPLOAD_PATH = os.path.join(BASE_DIR,MEDIA_ROOT)
#print(MEDIA_URL)
# Add static folder to Static dic
# STATICFILES_DIRS = [
# os.path.join(BASE_DIR, "static"),
# ]

# Redirect the mail url
# django.contrib.auth.LOGIN_URL = 'home'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = Config.get('SMTP', 'DEFAULT_FROM_EMAIL')
SERVER_EMAIL = Config.get('SMTP', 'SERVER_EMAIL')
EMAIL_HOST = Config.get('SMTP', 'EMAIL_HOST')
EMAIL_PORT = Config.get('SMTP', 'EMAIL_PORT')
EMAIL_HOST_USER = Config.get('SMTP', 'EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = Config.get('SMTP', 'EMAIL_HOST_PASSWORD')
EMAIL_BACKEND = Config.get('SMTP', 'EMAIL_BACKEND')

# Alchemy Service Credentials:-
# Alchemy_api_key = Config.get('ALCHEMY', 'ALCHEMY_KEY')
alchemy_username = Config.get('ALCHEMY', 'username')
alchmey_password = Config.get('ALCHEMY', 'password')

ml_url = Config.get('ML','URL')


