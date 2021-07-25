from .base import PromBase
from .factory import MetricsFactory

CREATE_DATE_PREFIX = 'create_data'


@MetricsFactory.set_metrics_cls(metrics_name=CREATE_DATE_PREFIX)
class CreateData(PromBase):

    def __init__(self, containerid: int = None):

        super(CreateData, self).__init__()

        self.containerid = containerid

    def get_last_call_name(self):

        return f'{CREATE_DATE_PREFIX}__last_call_{self.containerid}'

    def get_success_name(self):

        return f'{CREATE_DATE_PREFIX}__success_{self.containerid}'

    def get_exception_name(self):

        return f'{CREATE_DATE_PREFIX}__exception_{self.containerid}'

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
