
from .base import PromBase
from .factory import MetricsFactory

COMPUTE_DENDROGRAM_PREFIX = 'compute_dendrogram'


@MetricsFactory.set_metrics_cls(metrics_name='dendrogram')
class ComputeDendrogram(PromBase):

    def __init__(self, containerid: int = None):

        super(ComputeDendrogram, self).__init__()

        self.containerid = containerid

    def del_records(self):

        pass

    def response(self, value=None):

        return {
            'containerid': self.containerid,
            'ready': self.ready,
            'value': value,
            'msg': 'The response',
            'result': self.result
        }

    def exception_response(self, value: float = None):

        return {
            'containerid': self.containerid,
            'ready': self.ready,
            'value': value,
            'msg': 'An exception',
            'result': self.result
        }

    def no_results_response(self):

        return {
            'ready': self.ready,
            'result': self.result,
            'msg': 'no records in prometheus',
            'containerid': self.containerid
        }

    def get_last_call_name(self):

        return f'{COMPUTE_DENDROGRAM_PREFIX}__last_call_{self.containerid}'

    def get_success_name(self):

        return f'{COMPUTE_DENDROGRAM_PREFIX}__success_{self.containerid}'

    def get_exception_name(self):

        return f'{COMPUTE_DENDROGRAM_PREFIX}__exception_{self.containerid}'
