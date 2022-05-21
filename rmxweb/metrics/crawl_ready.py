
from .config import CREATE_DATA_PREFIX
from .query import LastCall


class CrawlReady(object):
    """
    Querying all metrics for the crawl/scrasync metrics
    """
    def __init__(self, containerid: int = None):
        """
        Instantiating the CrawlReady class.

        :param containerid:
        """
        self.stats = LastCall(
            dtype=CREATE_DATA_PREFIX,
            containerid=containerid
        )

    def __call__(self):
        return self.stats.status()
