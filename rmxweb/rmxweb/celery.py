
import os
from pathlib import Path

from celery import Celery

from . import celery_settings

BASE_DIR = Path(__file__).resolve().parent.parent

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rmxweb.settings')

# print('\n\n\n')
# print(BASE_DIR)
# sys.path.append(BASE_DIR)

celery = Celery('rmxweb')
celery.config_from_object(celery_settings)

# celery.autodiscover_tasks()
