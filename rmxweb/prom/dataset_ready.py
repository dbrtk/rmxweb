

from .config import CRAWL_CALLBACK_PREFIX, CRAWL_RUN_PREFIX
from .query import RunningProcess


class DatasetReady(object):

    def __init__(self, containerid: int):

        self.stats = RunningProcess(
            containerid=containerid,
            callback_dtype=CRAWL_CALLBACK_PREFIX,
            run_dtype=CRAWL_RUN_PREFIX
        )

    def __call__(self):
        return self.stats.stat_for_last_call()
