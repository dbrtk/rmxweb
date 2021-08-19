import time

import requests

from .base import BasePrometheus
from rmxweb.config import (
    PROMETHEUS_JOB, PROMETHEUS_URL, SECONDS_AFTER_LAST_CALL
)


class Query(object):

    def __init__(self):
        pass


class QueryPrometheus(BasePrometheus):
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
        super(QueryPrometheus, self).__init__(*args, **kwds)
        self.ready = False
        self.containerid = containerid
        self.features = features
        self.result = self.get_metrics()

    def prom_query(self):
        return '{{__name__=~"{success}|{lastcall}|{exception}",job="{job}"}}'\
            .format(
                success=self.success_name,
                exception=self.exception_name,
                lastcall=self.lastcall_name,
                job=PROMETHEUS_JOB
            )

    def get_metrics(self):
        q = self.prom_query()
        endpoint = f'http://{PROMETHEUS_URL}/query?query={q}'
        resp = requests.get(endpoint)
        resp = resp.json()
        return resp.get('data', {}).get('result', [])

    def __get_metrics(self):
        ready = False
        result = self.get_metrics()
        if not result:
            # This is returned when there are no results; the crawl is finished
            # and the container is ready.
            return {
                'ready': True,
                'result': result,
                'msg': 'no records in prometheus',
                'containerid': self.containerid
            }
        lastcall_obj = next(
            _ for _ in result
            if _.get('metric').get('__name__') == self.lastcall_name
        )
        lastcall_val = float(lastcall_obj['value'][1])
        if time.time() - SECONDS_AFTER_LAST_CALL > lastcall_val:
            ready = True
        return {
            'containerid': self.containerid,
            'ready': ready,
            'msg': 'crawl ready',
            'result': result
        }

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

        if not self.result:
            self.ready = True
            return self.no_results_response()

        last_call_rec = self.get_record(name=self.lastcall_name)
        if not last_call_rec:
            return self.no_results_response()
        last_call_val = float(last_call_rec['value'][1])
        if time.time() - self.time_after_last_call > last_call_val:
            self.ready = True
        return self.response()

    # def stat_for_running_process(
    #         self,
    #         run_dtype: str = None,
    #         callback_dtype: str = None
    # ):
    #     """
    #     Getting metrics for a process that calls a function on callback. This
    #     allows to check if a process started running and if it exited (with a
    #     call to the callback method).
    #
    #     :param run_dtype:
    #     :param callback_dtype:
    #     :return:
    #     """
    #     # todo(): delete
    #     pass

    # def check_last_call_exists(self):
    #     """This method checks if the records exists in prom."""
    #     # todo():  delete this
    #     exception = self.last_call_exception()
    #     if exception:
    #         value = float(exception['value'][1])
    #         return self.exception_response(value=value)
    #     if not self.result:
    #         self.ready = True
    #         return self.no_results_response()
    #     return self.response()

    def last_call_exception(self):
        """
        This is called when there is any `last_called` record in prometheus. It
        returns the value of the record that holds the exception.
        """
        exception = self.get_record(name=self.exception_name)
        if exception:
            value = float(exception['value'][1])
            return self.exception_response(value=value)
        return

    def last_call_success(self):
        """Returns the last success response."""
        success = self.get_record(name=self.success_name)
        if success:
            value = float(success['value'][1])
            return self.response(value=value)
        return

    def get_record(self, name: str = None):
        """
        :return:
        """
        try:
            return next(
                _ for _ in self.result
                if _.get('metric').get('__name__') == name
            )
        except StopIteration:
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
            'result': self.result,
            'msg': 'No records in prometheus.',
            'containerid': self.containerid
        }

    def exception_response(self, value: float = None):
        return {
            'containerid': self.containerid,
            'ready': self.ready,
            'value': value,
            'msg': 'There was an exception while processing your request',
            'error': True,
            'result': self.result
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
        # run stats
        self.rstat = QueryPrometheus(
            dtype=run_dtype,
            containerid=containerid,
            features=features,
            **kwds
        )
        # callback stats
        self.cstat = QueryPrometheus(
            dtype=callback_dtype,
            containerid=containerid,
            features=features,
            **kwds
        )
        print(
            f"\n\nMetrics for run: {self.rstat.result}\n"
            f"Metrics for callback: {self.cstat.result}"
        )

    def stat_for_last_call(self):
        c_success = self.cstat.get_record(self.cstat.success_name)
        if c_success:
            print(f"got c_success: {c_success} - it is computed")
            return {
                "ready": True,
                "record": c_success,
            }
        else:
            c_exception = self.cstat.get_record(self.cstat.exception_name)
            if c_exception:
                return self.exception_response(c_exception)
        r_success = self.rstat.get_record(self.rstat.success_name)
        if r_success:
            return {
                "ready": False,
                "message": "computing data",
                "record": r_success
            }
        if not r_success:
            r_exception = self.rstat.get_record(self.rstat.exception_name)
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
