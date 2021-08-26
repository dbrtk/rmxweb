import time

from .base import Namespace, Q
from rmxweb.config import SECONDS_AFTER_LAST_CALL


class LastCall(Namespace):
    """
    Querying Prometheus for metrics and stats.
    """

    def __init__(
            self,
            *args,
            containerid: (int, str) = None,
            features: int = None,
            time_after_last_call: int = SECONDS_AFTER_LAST_CALL,
            **kwds
    ):
        """
        :param args:
        :param containerid:
        :param features:
        :param kwds:
        """
        self.time_after_last_call = time_after_last_call
        super(LastCall, self).__init__(
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
        return self.enter_name, self.exit_name

    def status(self):
        """
        This method checks if a record exists in prom and if it was created
        less than 30 seconds ago. The time is defined in the
        `time_after_last_call` class variable.
        """
        if not self.q.result:
            self.ready = True
            return self.no_results_response()

        exit_record = self.q.get_record(name=self.exit_name)
        if not exit_record:
            enter_record = self.q.get_record(name=self.enter_name)
            if enter_record:
                if self.q.record_outdated(enter_record):
                    self.ready = True
                else:
                    self.ready = False
                return self.response(float(enter_record['value'][1]))

        exit_val = float(exit_record['value'][1])
        if time.time() - self.time_after_last_call > exit_val:
            self.ready = True
        return self.response(exit_val)

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


class RunningProcess(object):

    def __init__(
            self,
            run_dtype: str = None,
            callback_dtype: str = None,
            containerid: int = None,
            features: int = None,
            **kwds
    ):
        """

        :param run_dtype:
        :param callback_dtype:
        :param containerid:
        :param features:
        :param kwds:
        """
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
            self.run_n.enter_name,
            self.run_n.exit_name,
            self.callback_n.enter_name,
            self.callback_n.exit_name,
        )

    @staticmethod
    def resp_for_busy(record):
        """
        Response for status busy.

        :param record: record from prometheus
        :return:
        """
        return {
            "ready": False,
            "busy": True,
            "message": "computing data",
            "record": record
        }

    def status(self):
        """

        :return:
        """
        print(f"\n\n\ninside RunningProcess.status")
        print(f"run dtype: {self.run_n.dtype}")
        print(f"callback dtype: {self.callback_n.dtype}")
        c_exit = self.q.get_record(self.callback_n.exit_name)
        if c_exit:
            print(f"callback_exit -> ready: {c_exit}")
            return {
                "ready": True,
                "record": c_exit,
            }
        record = self.q.get_record(self.callback_n.enter_name) or \
            self.q.get_record(self.run_n.exit_name) or \
            self.q.get_record(self.run_n.enter_name)

        print(f"any other record: {record}")

        if record:
            if not self.q.record_outdated(record):
                print("record is valid -> busy")
                return self.resp_for_busy(record)

        print("No records in the data store -> ready\n\n\n")

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
