import time

from .base import Namespace, Q
from rmxweb.config import (
    PROMETHEUS_JOB,
    PROMETHEUS_URL,
    SECONDS_AFTER_LAST_CALL,
)


class QueryPrometheus(Namespace):
    """
    Querying Prometheus for metrics and stats.
    """
    time_after_last_call = SECONDS_AFTER_LAST_CALL

    def __init__(
            self,
            *args,
            containerid: (int, str) = None,
            features: int = None,
            **kwds
    ):
        """
        :param args:
        :param containerid:
        :param features:
        :param kwds:
        """
        super(QueryPrometheus, self).__init__(
            *args,
            containerid=containerid,
            features=features,
            **kwds
        )
        self.ready = False
        self.q = Q(metrics_names=self.metrics_names)

    @property
    def metrics_names(self):
        """
        Returns task names to query metrics on prometheus.
        :return:
        """
        return self.success_name, self.exception_name, self.lastcall_name

    def stat_for_last_call(self):
        """
        This method checks if a record exists in prom and if it was created
        less than 30 seconds ago. The time is defined in the
        `time_after_last_call` class variable.
        """
        exception = self.last_call_exception()
        if exception:
            value = float(exception['value'][1])
            return self.exception_response(value=value)

        if not self.q.result:
            self.ready = True
            return self.no_results_response()

        last_call_rec = self.q.get_record(name=self.lastcall_name)
        if not last_call_rec:
            return self.no_results_response()
        last_call_val = float(last_call_rec['value'][1])
        if time.time() - self.time_after_last_call > last_call_val:
            self.ready = True
        return self.response()

    def last_call_exception(self):
        """
        This is called when there is any `last_called` record in prometheus. It
        returns the value of the record that holds the exception.
        """
        exception = self.q.get_record(name=self.exception_name)
        if exception:
            value = float(exception['value'][1])
            return self.exception_response(value=value)
        return

    def last_call_success(self):
        """Returns the last success response."""
        success = self.q.get_record(name=self.success_name)
        if success:
            value = float(success['value'][1])
            return self.response(value=value)
        return

    def response_message(self):
        return f"The requested dataset is " \
               f"{'ready' if self.ready else 'being computed'}."

    def response(self, value: float = None):
        """
        :param value:
        :return:
        """
        return {
            'containerid': self.containerid,
            'ready': self.ready,
            'busy': not self.ready,
            'value': value,
            'msg': self.response_message()
        }

    def no_results_response(self):
        """
        This is returned when there are no results; the crawl is finished and
        the container is ready.

        :return: dict
        """
        return {
            'ready': self.ready,
            'result': self.q.result,
            'msg': 'No records in prometheus.',
            'containerid': self.containerid
        }

    def exception_response(self, value: float = None):
        """
        Returns an exception response.

        :param value:
        :return:
        """
        return {
            'containerid': self.containerid,
            'ready': self.ready,
            'value': value,
            'msg': 'There was an exception while processing your request',
            'error': True,
            'result': self.q.result
        }


class RunProcessMetrics(object):

    def __init__(
            self,
            run_dtype: str = None,
            callback_dtype: str = None,
            containerid: int = None,
            features: int = None,
            **kwds
    ):
        # run namespace
        self.run_n = Namespace(
            dtype=run_dtype,
            containerid=containerid,
            features=features,
            **kwds
        )
        # callback namespace
        self.callback_n = Namespace(
            dtype=callback_dtype,
            containerid=containerid,
            features=features,
            **kwds
        )
        self.q = Q(metrics_names=self.metrics_names)

    @property
    def metrics_names(self):

        return (
            self.run_n.lastcall_name,
            self.run_n.success_name,
            self.run_n.exception_name,
            self.callback_n.lastcall_name,
            self.callback_n.exception_name,
            self.callback_n.success_name,
        )

    def stat_for_last_call(self):
        """

        :return:
        """
        c_success = self.q.get_record(self.callback_n.success_name)
        if c_success:
            return {
                "ready": True,
                "record": c_success,
            }
        else:
            c_exception = self.q.get_record(self.callback_n.exception_name)
            if c_exception:
                return self.exception_response(c_exception)

        r_success = self.q.get_record(self.run_n.success_name)
        if r_success:
            if not self.record_outdated(r_success):
                return {
                    "ready": False,
                    "message": "computing data",
                    "record": r_success
                }
        else:
            r_exception = self.q.get_record(self.run_n.exception_name)
            if r_exception:
                return self.exception_response(r_exception)
        return {
            "ready": True,
            "message": "No records in prometheus!"
        }

    @staticmethod
    def exception_response(record):
        return {
            "ready": False,
            "message": "exception",
            "record": record
        }

    @staticmethod
    def record_outdated(record):
        """
        Checks if the difference between the timestamp in the record and now is
        greater than 15 minutes.
        The second value in a prom's sample is a timestamp.

        :param record:
        :return:
        """
        now = time.time()
        timestamp = record['value'][1]
        if not isinstance(timestamp, float):
            timestamp = float(timestamp)
        if now - timestamp >= 15 * 60:
            return True
        return False
