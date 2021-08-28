
from prom.config import (
    COMPUTE_DENDROGRAM_CALLBACK_PREFIX,
    COMPUTE_MATRIX_CALLBACK_PREFIX,
)
from prom.decorator import register_with_prom
from rmxweb.celery import celery


@celery.task
@register_with_prom(COMPUTE_MATRIX_CALLBACK_PREFIX)
def compute_matrix_callback(
        containerid: int = None,
        features: int = None,
        **kwds
):
    """
    This task is called by nlp. It is called after nlp finishes computing a
    matrix, a graph. This function is just a placeholder for Prometheus. It
    does logging.

    :param containerid:
    :param features:
    """
    pass


@celery.task
@register_with_prom(COMPUTE_DENDROGRAM_CALLBACK_PREFIX)
def compute_dendrogram_callback(containerid: int = None):
    """Called when the dendrogram is computed. It needs to be here for prom."""
    pass
