"""Emitting miscellaneous messages to the world (other services) through
   celery/rabbitmq.
"""

from rmxweb.celery import celery
from rmxweb.config import NLP_TASKS


def get_available_features(containerid, folder_path):
    """Retrieves available features from nlp"""
    result = celery.send_task(
        NLP_TASKS['available_features'],
        kwargs={'corpusid': containerid, 'path': folder_path}).get()
    return result

