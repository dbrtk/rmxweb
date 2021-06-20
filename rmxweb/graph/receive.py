
from prom.dendrogram import ComputeDendrogram, COMPUTE_DENDROGRAM_PREFIX
from prom.metrics import trackprogress
from rmxweb.celery import celery


@celery.task
@trackprogress(dtype=COMPUTE_DENDROGRAM_PREFIX)
def compute_dendrogram(containerid: int = None):
    """Called when NLP starts computing the dendrogram. It is called before a
    task is sent to NLP.

    This function is a placeholder; it is used to make sure that the progress
    is tracked by prometheus. So, it is decorated with trackprogress.
    """
    return


@celery.task
def compute_dendrogram_callback(containerid: int = None):
    """Called when the dendrogram is computed."""
    inst = ComputeDendrogram(containerid=containerid)
