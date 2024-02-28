from unittest.mock import DEFAULT
from .base import *


DEBUG = True
# MEDIA_ROOT = os.path.join(BASE_DIR, 'file')
# FULL_MEDIA_ROOT = os.path.join(MEDIA_ROOT, 'file')
# ALLOWED_HOSTS = []

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fileup',
        'USER': 'yuitech',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '3315',
    },
    'user': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'portal',
        'USER': 'yuitech',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '3313',
    }
}

# 利用するRouter, manage.pyから見ての相対パス
DATABASE_ROUTERS = [
    'routers.AuthRouter',
]

# アプリケーションごとの接続先DBのマッピング
DATABASE_APPS_MAPPING = {
    # defaultには管理系のTable
    'admin'              : 'user',
    'auth'               : 'user',
    'contenttypes'       : 'user',
    'sessions'           : 'user',
    'messages'           : 'default',
    'staticfiles'        : 'default',
    # 'django_celery_beat' : 'default',
    # userにはユーザー系処理
    'accounts'          : 'user',
    'contracts'         : 'user',
    # defaultには契約関連のTable
    'draganddrop'         : 'default',

}
# LOGIN_URL = 'register:login'
# LOGIN_REDIRECT_URL = 'register:top'

#メールをコンソールに表示する
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATIC_URL = '/static/'

# アプリケーションに紐付かない静的ファイルの置き場所（プロジェクト直下のstaticディレクトリを示す）
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# プロジェクト直下にmediaフォルダが作成される BASE_DIR(C:\Users\user\Dropbox\08.開発\training_pj)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ファイル削除用にパスを作成 MEDIA_ROOT(C:\Users\user\Dropbox\08.開発\training_pj\media)
FULL_MEDIA_ROOT = os.path.join(MEDIA_ROOT, 'uploads')

# 動画ファイル削除用にパスを作成 FULL_MEDIA_ROOT(C:\Users\user\Dropbox\08.開発\training_pj\media\uploads)
MOVIE_FULL_MEDIA_ROOT = os.path.join(FULL_MEDIA_ROOT, 'movie')

# アップロードファイルにはFQDN+/media/+uploads+ファイル名でアクセスする
MEDIA_URL = '/media/'

# # リソース管理テーブル用、トレーニングのサイズ 1トレーニング=20KB(=20480B)
# TRAINING_SIZE = 20480

# # リソース管理テーブル用、デフォルトで設定しているポスターのサイズ
# DEFAULT_POSTER = 377487

# # リソース管理テーブル用、デフォルトで設定しているコースのポスターのサイズ
# DEFAULT_SUBJECT_POSTER = 3187

# X_FRAME_OPTIONS = 'ALLOWALL'

# XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'local': {
            'format': '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'local',
        },
    },
    'loggers': {
        # 自作したログ出力
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Djangoのエラー・警告・開発WEBサーバのアクセスログ
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # 実行SQL
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}



#上原さんのやつ　新　2024
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'production': {
#             'format': '%(asctime)s [%(levelname)s] %(process)d %(thread)d '
#                     '%(pathname)s:%(lineno)d %(message)s'
#         },
#     },
#     'handlers': {
#         'file': {
#             'class': 'logging.FileHandler',
#             'filename': 'logs/django.log', 
#             'formatter': 'production',
#             'level': 'DEBUG',
#         },
#     },
#     'loggers': {
#         # 自作したログ出力
#         '': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#         # Djangoの警告・エラー
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#     },
# }
