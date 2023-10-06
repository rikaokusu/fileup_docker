"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import sys
import os
from pathlib import Path

# メッセージのclassを定義する(サーバサイドからフロントへのメッセージ)
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_uzzedvq)xcf_-ybo%e6f(gk2d5ho$2bexp9#-k-m43qxtq%n!'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'draganddrop',
    'accounts',
    'bootstrap_datepicker_plus',
    'django.forms',
    # 'django.contrib.sessions',
    # アカウント移植
    'contracts',
    'betterforms',
    'webpack_loader',
    'widget_tweaks',
    'mathfilters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'BASE_DIR'/'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ja'
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

# アプリケーションに紐付かない静的ファイルの置き場所（プロジェクト直下のstaticディレクトリを示す）
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# アプリケーションディレクトリをプロジェクト直下のappsフォルダにまとめる
sys.path.append(os.path.join(BASE_DIR, 'apps'))

MEDIA_ROOT = os.path.join(BASE_DIR, 'file')
MEDIA_URL = '/file/'
FULL_MEDIA_ROOT = os.path.join(MEDIA_ROOT, 'file')

#自分で作ったUserモデルをデフォルトで使用するように宣言
# accountsというアプリケーションです
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
# LOGOUT_URL = 'accounts:top'
LOGIN_REDIRECT_URL = 'draganddrop:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'


# FORMでチェックボックスをカスタマイズする場合に追加
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


# メッセージをサーバサイドからフロントへ送信する際の保存先？
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
MESSAGE_TAGS = {
    message_constants.SUCCESS: 'alert alert-success',
    message_constants.ERROR: 'alert alert-danger',
}

# WebPackを読むための設定
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}


DEFAULT_RECORD_SIZE=20480 #20KB