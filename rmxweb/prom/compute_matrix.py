#
# from .track_progress import QueryPrometheus
# from .factory import MetricsFactory
#
# COMPUTE_MATRIX_PREFIX = 'compute_matrix'
#
# # todo(): delete the module
#
# @MetricsFactory.set_metrics_cls(metrics_name=COMPUTE_MATRIX_PREFIX)
# class ComputeMatrix(QueryPrometheus):
#
#     prefix = COMPUTE_MATRIX_PREFIX
#
#     def response_message(self):
#         return f"The matrices to display the graph are " \
#                f"{'ready' if self.ready else 'being computed'}."
