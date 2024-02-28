from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# LOGIN_URL = 'register:login'
# LOGIN_REDIRECT_URL = 'register:top'


#お知らせ内容を実際にメールに送信する
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DATABASES = {
    # fileupの設定
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fileup',
        'USER': 'yuitech',
        'PASSWORD':'password',
        'HOST':'db_fileup',# docker-compose.ymlで設定した名前を設定
        'PORT': '3306',
    },
    # ポータルの設定 ※ポータルで認証を行う場合に必要
    'user': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'portal',
        'USER': 'yuitech',
        'PASSWORD': 'password',
        'HOST': 'db',
        'PORT': '3306',
    }

}

# # collectstaticで集められるディレクトリ。Nginxの指定と合わせる
STATIC_ROOT = '/static/'


# 以下、ポータルで認証を行うための設定をdocker化前のまなもあから移植

# 利用するRouter, manage.pyから見ての相対パス
DATABASE_ROUTERS = [
    'routers.AuthRouter',
]

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
    'bulk'              : 'user',
    'contracts'         : 'user',
    # defaultには契約関連のTable
    'draganddrop'         : 'default',
}

STATIC_URL = '/static/'

# アプリケーションに紐付かない静的ファイルの置き場所（プロジェクト直下のstaticディレクトリを示す）
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# プロジェクト直下にmediaフォルダが作成される BASE_DIR(C:\Users\user\Dropbox\08.開発\training_pj)
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_ROOT = '/'
MEDIA_ROOT = '/media/'


# ファイル削除用にパスを作成 MEDIA_ROOT(C:\Users\user\Dropbox\08.開発\training_pj\media)
FULL_MEDIA_ROOT = os.path.join(MEDIA_ROOT, 'uploads')
# ファイル削除用にパスを作成(無課金アップロード前)
FULL_MEDIA_ROOT_FREETMP = os.path.join(MEDIA_ROOT, 'free_tmp')
# ファイル削除用にパスを作成(無課金アップロード後)
FULL_MEDIA_ROOT_FREE = os.path.join(MEDIA_ROOT, 'free')
# ファイル削除用にパスを作成(課金アップロード前)
FULL_MEDIA_ROOT_PAYTMP = os.path.join(MEDIA_ROOT, 'pay_tmp')
# ファイル削除用にパスを作成(課金アップロード後)
FULL_MEDIA_ROOT_PAY = os.path.join(MEDIA_ROOT, 'pay')



# 動画ファイル削除用にパスを作成 FULL_MEDIA_ROOT(C:\Users\user\Dropbox\08.開発\training_pj\media\uploads)
MOVIE_FULL_MEDIA_ROOT = os.path.join(FULL_MEDIA_ROOT, 'movie')

# アップロードファイルにはFQDN+/media/+uploads+ファイル名でアクセスする
# MEDIA_URL = '/'
MEDIA_URL = '/media/'


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