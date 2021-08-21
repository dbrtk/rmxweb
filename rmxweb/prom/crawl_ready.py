
from .config import CREATE_DATA_PREFIX
from .query import QueryPrometheus


class CrawlReady(object):

    def __init__(self, containerid: int = None, features: int = None):
        self.stats = QueryPrometheus(
            dtype=CREATE_DATA_PREFIX,
            containerid=containerid,
            features=features
        )

    def __call__(self):
        return self.stats.stat_for_last_call()
