
from .config import CREATE_DATA_PREFIX
from .query import QueryPrometheus


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
    def __init__(self, containerid: int = None):
        self.stats = QueryPrometheus(
            dtype=CREATE_DATA_PREFIX,
            containerid=containerid,
        )

    def __call__(self):
        return self.stats.stat_for_last_call()
