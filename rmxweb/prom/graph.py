
from .config import COMPUTE_MATRIX_CALLBACK_PREFIX, COMPUTE_MATRIX_RUN_PREFIX
from .query import RunningProcess


class GraphReady(object):

    def __init__(self, containerid: int = None, features: int = None):
        self.stats = RunningProcess(
            callback_dtype=COMPUTE_MATRIX_CALLBACK_PREFIX,
            run_dtype=COMPUTE_MATRIX_RUN_PREFIX,
            containerid=containerid,
            features=features
        )

    def __call__(self, *args, **kwargs):
        return self.stats.status()
