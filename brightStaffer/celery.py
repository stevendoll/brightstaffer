from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from configparser import ConfigParser
from brightStaffer.settings import BASE_DIR

CONFIG_FILE_NAME = 'brightstaffer.ini'
Config = ConfigParser()
config_file_path = os.path.join(BASE_DIR, 'brightStaffer', CONFIG_FILE_NAME)
Config.read(config_file_path)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', Config.get('DATABASE CONNECTIONS', 'DJANGO_SETTINGS_MODULE'))
app = Celery('brightStaffer')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


