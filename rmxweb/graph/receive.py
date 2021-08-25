
from prom.config import (
    COMPUTE_DENDROGRAM_CALLBACK_PREFIX,
    COMPUTE_DENDROGRAM_RUN_PREFIX,
    COMPUTE_MATRIX_CALLBACK_PREFIX,
)
from prom.decorator import register_with_prom
from rmxweb.celery import celery


@celery.task
@register_with_prom(dtype=COMPUTE_MATRIX_CALLBACK_PREFIX)
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
    # print(
    #     f"compute_matrix_callback called with containerid: {containerid}; "
    #     f"features: {features}; kwds: {kwds}"
    # )
    pass


@celery.task
@register_with_prom(dtype=COMPUTE_DENDROGRAM_RUN_PREFIX)
def compute_dendrogram_run(containerid: int = None):
    """
    This task is a placeholder used by prom's register_with_prom decorator.
    :param containerid:
    :return:
    """
    pass


@celery.task
@register_with_prom(dtype=COMPUTE_DENDROGRAM_CALLBACK_PREFIX)
def compute_dendrogram_callback(containerid: int = None):
    """Called when the dendrogram is computed. It needs to be here for prom."""
    # print(
    #     f"Called `compute_dendrogram_callback` with containerid: {containerid}"
    #     f"COMPUTE_DENDROGRAM_CALLBACK_PREFIX: {COMPUTE_DENDROGRAM_CALLBACK_PREFIX}"
    # )
    pass
