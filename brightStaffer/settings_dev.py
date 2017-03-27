try:
    from brightStaffer.settings import *
except ImportError as e:
    pass

from datetime import timedelta
from configparser import ConfigParser
CONFIG_FILE_NAME = 'brightstaffer.ini'
Config = ConfigParser()
config_file_path = os.path.join(BASE_DIR, 'brightStaffer', CONFIG_FILE_NAME)
Config.read(config_file_path)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': Config.get('DATABASE CONNECTIONS', 'DB_DATABASE'),
        'USER': Config.get('DATABASE CONNECTIONS', 'DB_USERNAME'),
        'PASSWORD': Config.get('DATABASE CONNECTIONS', 'DB_PASSWORD'),
        'HOST': Config.get('DATABASE CONNECTIONS', 'DB_HOST'),
        'PORT': Config.get('DATABASE CONNECTIONS', 'DB_PORT')
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': Config.get('HAYSTACK CONNECTIONS', 'HAYSTACK_URL'),
        'INDEX_NAME': Config.get('HAYSTACK CONNECTIONS', 'HAYSTACK_INDEX_NAME'),
        'INCLUDE_SPELLING': True,
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

BROKER_URL = Config.get('REDIS CONNECTIONS', 'BROKER_URL')
CELERY_RESULT_BACKEND = Config.get('REDIS CONNECTIONS', 'CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = Config.get('REDIS CONNECTIONS', 'CELERY_ACCEPT_CONTENT')
CELERY_TASK_SERIALIZER = Config.get('REDIS CONNECTIONS', 'CELERY_TASK_SERIALIZER')
CELERY_RESULT_SERIALIZER = Config.get('REDIS CONNECTIONS', 'CELERY_RESULT_SERIALIZER')
CELERY_TIMEZONE = Config.get('REDIS CONNECTIONS', 'CELERY_TIMEZONE')

CELERYBEAT_SCHEDULE = {
    "run-every-30-minutes": {
            "task": "brightStafferapp.tasks.update_indexes",
            "schedule": timedelta(minutes=1),
        },
    "run-every-1-minutes": {
                "task": "brightStafferapp.tasks.add",
                "schedule": timedelta(seconds=10),
                "args": (16, 16)
            },
}