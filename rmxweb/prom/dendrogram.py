
from .base import PromBase
from .factory import MetricsFactory
from .incremental import Incremental

COMPUTE_DENDROGRAM_PREFIX = 'dendrogram'


@MetricsFactory.set_metrics_cls(metrics_name=COMPUTE_DENDROGRAM_PREFIX)
class ComputeDendrogram:

    def __init__(self, containerid: int = None, label: str = None):
        self.containerid = containerid
        self.metrics = Incremental(
            self.containerid, dtype=COMPUTE_DENDROGRAM_PREFIX, label=label
        )
        self.v = None
        self.ready = self.is_ready()

    def is_ready(self):
        self.v = self.metrics.get_value()
        if self.v == 0:
            return True
        return False

    def response(self):
        return {
            'containerid': self.containerid,
            'ready': self.ready,
            'busy': not self.ready,
            'value': self.v,
            'msg': f'The dendrogram is '
                   f'{"ready" if self.ready else "being computed"}.'
        }


class DepprComputeDendrogram(PromBase):
    # todo(): delete this class!
    def __init__(self, containerid: int = None):

        self.containerid = containerid

        super().__init__()

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
            'msg': 'Exception',
            'error': True,
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
