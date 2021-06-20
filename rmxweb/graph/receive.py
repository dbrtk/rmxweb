
from container.models import FeaturesStatus

from rmxweb.celery import celery


@celery.task
def compute_dendrogram(containerid: int = None):
    """Called when NLP starts computing the dendrogram. It is called before a
    task is sent to NLP.
    """
    FeaturesStatus.set_status_dendrogram(containerid=containerid)


@celery.task
def compute_dendrogram_callback(containerid: int = None):
    """Called when the dendrogram is computed."""
    FeaturesStatus.del_status_dendrogram(containerid=containerid)
