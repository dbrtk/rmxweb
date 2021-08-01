
from .base import BaseIncremental
from .factory import MetricsFactory

COMPUTE_MATRIX_PREFIX = 'compute_matrix'


@MetricsFactory.set_metrics_cls(metrics_name=COMPUTE_MATRIX_PREFIX)
class ComputeMatrix(BaseIncremental):

    prefix = COMPUTE_MATRIX_PREFIX

    def response(self):
        return {
            'containerid': self.containerid,
            'ready': self.ready,
            'busy': not self.ready,
            'value': self.v,
            'msg': f'The matrices to display the graph is '
                   f'{"ready" if self.ready else "being computed"}.'
        }
