
from .config import INTEGRITY_CHECK_CALLBACK_PREFIX, INTEGRITY_CHECK_RUN_PREFIX
from .query import RunProcessMetrics


class IntegrityCheckReady(object):

    def __init__(self, containerid: int = None, features: int = None):
        self.stats = RunProcessMetrics(
            containerid=containerid,
            features=features,
            callback_dtype=INTEGRITY_CHECK_CALLBACK_PREFIX,
            run_dtype=INTEGRITY_CHECK_RUN_PREFIX
        )

    def __call__(self):
        return self.stats.stat_for_last_call()
