
from .config import INTEGRITY_CHECK_CALLBACK_PREFIX, INTEGRITY_CHECK_RUN_PREFIX
from .query import RunningProcess


class IntegrityCheckReady(object):

    def __init__(self, containerid: int = None):
        self.stats = RunningProcess(
            containerid=containerid,
            callback_dtype=INTEGRITY_CHECK_CALLBACK_PREFIX,
            run_dtype=INTEGRITY_CHECK_RUN_PREFIX
        )

    def __call__(self):
        return self.stats.status()
