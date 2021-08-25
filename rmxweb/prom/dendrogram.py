
from .config import (
    COMPUTE_DENDROGRAM_CALLBACK_PREFIX,
    COMPUTE_DENDROGRAM_RUN_PREFIX
)
from .query import RunningProcess


class DendrogramReady(object):

    def __init__(self, containerid: int = None):
        self.stats = RunningProcess(
            run_dtype=COMPUTE_DENDROGRAM_RUN_PREFIX,
            callback_dtype=COMPUTE_DENDROGRAM_CALLBACK_PREFIX,
            containerid=containerid
        )

    def __call__(self, *args, **kwargs):
        return self.stats.status()
