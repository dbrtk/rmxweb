
from .config import (
    COMPUTE_DENDROGRAM_CALLBACK_PREFIX,
    COMPUTE_DENDROGRAM_RUN_PREFIX
)
from .query import RunProcessMetrics


class DendrogramReady(object):

    def __init__(self, containerid: int = None):
        self.stats = RunProcessMetrics(
            run_dtype=COMPUTE_DENDROGRAM_RUN_PREFIX,
            callback_dtype=COMPUTE_DENDROGRAM_CALLBACK_PREFIX,
            containerid=containerid
        )

    def __call__(self, *args, **kwargs):
        return self.stats.stat_for_last_call()