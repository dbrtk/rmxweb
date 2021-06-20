
import abc
import time

import requests

from rmxweb.config import (PROMETHEUS_JOB, PROMETHEUS_URL,
                           SECONDS_AFTER_LAST_CALL)


COMPUTE_DENDROGRAM_PREFIX = 'compute_dendrogram'


class PromBase(abc.ABC):

    time_after_last_call = SECONDS_AFTER_LAST_CALL

    def __init__(self):

        self.ready = False
        self.result = None

        self.success_name = self.get_success_name()
        self.exception_name = self.get_exception_name()
        self.last_call_name = self.get_last_call_name()

    def __call__(self, *args, **kwargs):

        pass

    def query(self):

        return '{{__name__=~"{success}|{lastcall}|{exception}",job="{job}"}}' \
            .format(
                success=self.success_name,
                exception=self.exception_name,
                lastcall=self.last_call_name,
                job=PROMETHEUS_JOB
            )

    def delete(self):
        """Deletes records from prometheus.
        :return:
        """
        endpoint = 'http://{}/admin/tsdb/delete_series?match={}'.format(
            PROMETHEUS_URL, self.query()
        )
        requests.post(endpoint)

    def get(self):

        endpoint = f'http://{PROMETHEUS_URL}/query?query={self.query()}'
        resp = requests.get(endpoint)
        resp = resp.json()
        return resp.get('data', {}).get('result', [])

    def stat_for_last_call(self):

        self.result = self.get()
        if not self.result:
            self.ready = True
            return self.no_results_response()

        last_call_rec = self.get_record(name=self.last_call_name)
        if not last_call_rec:
            return self.last_call_exception()
        last_call_val = float(last_call_rec['value'][1])
        if time.time() - self.time_after_last_call > last_call_val:
            self.ready = True
            # todo(): delete records in prom
            self.delete()
        return self.response()

    def last_call_exception(self):
        """This is called when there is any `last_called` record in prometheus.
        """
        exception = self.get_record(name=self.exception_name)
        if exception:
            value = float(exception['value'][1])
            return self.exception_response(value=value)
        success = self.get_record(name=self.success_name)
        if success:
            value = float(success['value'][1])
            return self.response(value=value)

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

    @abc.abstractmethod
    def response(self, value: float = None):
        """
        :return: dict
        """
        raise NotImplementedError('a `response` method is required')

    @abc.abstractmethod
    def no_results_response(self):
        """
        This is returned when there are no results; the crawl is finished and
        the container is ready.
        :return: dict
        """
        raise NotImplementedError('a `no_results_response` method is required')

    @abc.abstractmethod
    def exception_response(self, value: float = None):

        raise NotImplementedError('an `exception_response` method is required')

    @abc.abstractmethod
    def get_last_call_name(self):

        raise NotImplementedError('a `get_last_call_name` method is required')

    @abc.abstractmethod
    def get_success_name(self):

        raise NotImplementedError('a `get_success_name` method is required')

    @abc.abstractmethod
    def get_exception_name(self):

        raise NotImplementedError('a `get_exception_name` method is required')
