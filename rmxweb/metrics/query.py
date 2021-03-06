import time

from .namespace import Namespace, Q
from rmxweb.config import SECONDS_AFTER_LAST_CALL


class LastCall(Namespace):
    """
    Querying Redis for metrics and stats.
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
        Returns task names to query metrics in redis.
        :return:
        """
        return self.enter_name, self.exit_name

    def status(self):
        """
        This method checks if a record exists in redis and if it was created
        less than 30 seconds ago. The time is defined in the
        `time_after_last_call` class variable.
        """
        if not self.q.result:
            self.ready = True
            return self.no_results_response()

        exit_time = self.q.result.get(self.exit_name)
        if not exit_time:
            enter_time = self.q.result.get(self.enter_name)
            if enter_time:
                if self.q.record_outdated(enter_time):
                    self.ready = True
                    self.q.del_record(self.enter_name)
                else:
                    self.ready = False
                return self.response(enter_time)

        if not isinstance(exit_time, float):
            exit_time = float(exit_time)
        if time.time() - self.time_after_last_call > exit_time:
            self.ready = True
            self.q.del_record(self.exit_name)
        else:
            self.ready = False
        return self.response(exit_time)

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
            'msg': 'No records in redis.',
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
    def resp_for_busy(timestamp):
        """
        Response for status busy.

        :param timestamp: the timestamp
        :return:
        """
        return {
            "ready": False,
            "busy": True,
            "message": "computing data",
            "record": timestamp
        }

    def status(self):
        """

        :return:
        """
        c_exit = self.q.result.get(self.callback_n.exit_name)

        if c_exit:
            return {
                "ready": True,
                "record": c_exit,
            }
        c_enter = self.q.result.get(self.callback_n.enter_name)
        r_enter = self.q.result.get(self.run_n.enter_name)
        r_exit = self.q.result.get(self.run_n.exit_name)
        record = None
        if c_enter and not self.q.record_outdated(c_enter):
            record = c_enter
        elif r_exit and not self.q.record_outdated(r_exit):
            record = r_exit
        elif r_enter and not self.q.record_outdated(r_enter):
            record = r_enter
        if record:
            return self.resp_for_busy(record)
        for key in self.metrics_names:
            self.q.del_record(key)
        return {
            "ready": True,
            "message": "No records in redis!"
        }

    @staticmethod
    def exception_response(record):
        return {
            "ready": False,
            "message": "exception",
            "record": record
        }
