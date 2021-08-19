
from prom.config import (
    COMPUTE_DENDROGRAM_CALLBACK_PREFIX, COMPUTE_DENDROGRAM_RUN_PREFIX
)
from prom.decorator import trackprogress
from rmxweb.celery import celery


@celery.task
@trackprogress(dtype=COMPUTE_DENDROGRAM_RUN_PREFIX)
def compute_dendrogram(containerid: int = None):
    """Called when NLP starts computing the dendrogram. It is called before a
    task is sent to NLP.

    This function is a placeholder; it is used to make sure that the progress
    is tracked by prometheus. So, it is decorated with prom's track_progress.
    """
    print(
        f"Called `compute_dendrogram` with containerid: {containerid}"
    )
    return


@celery.task
@trackprogress(dtype=COMPUTE_DENDROGRAM_CALLBACK_PREFIX)
def compute_dendrogram_callback(containerid: int = None):
    """Called when the dendrogram is computed. It needs to be here for prom."""
    print(
        f"Called `compute_dendrogram_callback` with containerid: {containerid}"
    )
    return
