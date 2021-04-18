
import os

from celery import Celery

from . import celery_settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rmxweb.settings')

celery = Celery('rmxweb')
celery.config_from_object(celery_settings)

