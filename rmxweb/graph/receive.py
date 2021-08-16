
from prom.config import COMPUTE_DENDROGRAM_PREFIX
from prom.decorator import track_progress
from rmxweb.celery import celery


@celery.task
def compute_dendrogram(containerid: int = None):
    """Called when NLP starts computing the dendrogram. It is called before a
    task is sent to NLP.

    This function is a placeholder; it is used to make sure that the progress
    is tracked by prometheus. So, it is decorated with prom's track_progress.
    """
    return


@celery.task
@track_progress(dtype=COMPUTE_DENDROGRAM_PREFIX)
def compute_dendrogram_callback(containerid: int = None):
    """Called when the dendrogram is computed."""
    return
