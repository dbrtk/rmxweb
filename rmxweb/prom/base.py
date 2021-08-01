"""The base class for all classes handling prometheus metrics.
"""
import abc
import time

import requests

from .incremental import Incremental
from rmxweb.config import (PROMETHEUS_JOB, PROMETHEUS_URL,
                           SECONDS_AFTER_LAST_CALL)


COMPUTE_DENDROGRAM_PREFIX = 'compute_dendrogram'


class PromBase(abc.ABC):
    """
    Base class for prometheus clients.
    """
    time_after_last_call = SECONDS_AFTER_LAST_CALL

    def __init__(self):

        self.ready = False

        self.success_name = self.get_success_name()
        self.exception_name = self.get_exception_name()
        self.last_call_name = self.get_last_call_name()

        self.result = self.get()

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

    def del_query(self):
        """Query for deleting series in prom."""
        pass

    def delete(self):
        """Deletes records from prometheus.
        :return:
        """
        print('deleting the stats')
        endpoint = 'http://{}/admin/tsdb/delete_series?match={}'.format(
            PROMETHEUS_URL, self.query()
        )
        print(f'endpoint: {endpoint}')

        resp = requests.post(endpoint)
        print(resp)
        print(resp.json())

    def get(self):

        endpoint = f'http://{PROMETHEUS_URL}/query?query={self.query()}'
        resp = requests.get(endpoint)
        resp = resp.json()
        return resp.get('data', {}).get('result', [])

    def stat_for_last_call(self):
        """This method checks if a record exists in prom and if it was created
        less than 30 seconds ago. The time is defined in the
        `time_after_last_call` class variable.
        """
        exception = self.last_call_exception()
        if exception:
            return self.exception_response(value=exception)

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

    def check_last_call_exists(self):
        """This method checks if the records exists in prom."""
        exception = self.last_call_exception()
        if exception:
            return self.exception_response(value=exception)
        if not self.result:
            self.ready = True
            return self.no_results_response()
        return self.response()

    def last_call_exception(self):
        """This is called when there is any `last_called` record in prometheus.
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


class BaseIncremental(abc.ABC):

    prefix = None

    def __init__(self, containerid: int = None, label: str = None):
        self.containerid = containerid
        self.metrics = Incremental(
            self.containerid, dtype=self.prefix, label=label
        )
        self.v = None
        self.ready = self.is_ready()

    def is_ready(self):
        self.v = self.metrics.get_value()
        if self.v == 0:
            return True
        return False
