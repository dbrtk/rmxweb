
from .config import COMPUTE_MATRIX_CALLBACK_PREFIX, COMPUTE_MATRIX_RUN_PREFIX
from .query import RunProcessMetrics


class GraphReady(object):

    def __init__(self, containerid: int = None, features: int = None):
        self.stats = RunProcessMetrics(
            callback_dtype=COMPUTE_MATRIX_CALLBACK_PREFIX,
            run_dtype=COMPUTE_MATRIX_RUN_PREFIX,
            containerid=containerid,
            features=features
        )

    def __call__(self, *args, **kwargs):
        return self.stats.stat_for_last_call()
