

from .config import CRAWL_CALLBACK_PREFIX, CRAWL_RUN_PREFIX
from .query import RunningProcess


class DatasetReady(object):

    def __init__(self, containerid: int = None):

        self.stats = RunningProcess(
            containerid=containerid,
            callback_dtype=CRAWL_CALLBACK_PREFIX,
            run_dtype=CRAWL_RUN_PREFIX
        )

    def __call__(self):
        return self.stats.status()
