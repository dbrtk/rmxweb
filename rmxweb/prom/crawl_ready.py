
from .config import CREATE_DATA_PREFIX
from .query import QueryPrometheus
from rmxweb.config import CRAWL_MONITOR_COUNTDOWN, SECONDS_AFTER_LAST_CALL


class CrawlReady(object):
    """
    Querying all metrics for the crawl/scrasync metrics
    The response returned by prom:
    {
        'status': 'success',
        'data': {
            'resultType': 'vector',
            'result': [{
                'metric': {
                    '__name__': 'create_from_webpage__lastcall_<containerid>',
                    'job': 'scrasync'
                },
                'value': [1613125321.823, '1613125299.354587']
            }, {
                'metric': {
                    '__name__': 'create_from_webpage__succes_<containerid>',
                    'job': 'scrasync'
                }, 'value': [1613125321.823, '1613125299.3545368']
            }]
        }
    }
    """
    def __init__(self, containerid: int = None, client_request: bool = False):
        """

        :param containerid:
        :param client_request:
        """
        if client_request:
            # making a delay for requests made by the client. This is to ensure
            # that the integrity check records are in prometheus before
            # returning an object that contains ready set to True.
            time_after_last_call = CRAWL_MONITOR_COUNTDOWN +\
                                   SECONDS_AFTER_LAST_CALL + 5
        else:
            time_after_last_call = SECONDS_AFTER_LAST_CALL
        self.stats = QueryPrometheus(
            dtype=CREATE_DATA_PREFIX,
            containerid=containerid,
            time_after_last_call=time_after_last_call
        )

    def __call__(self):
        return self.stats.stat_for_last_call()
