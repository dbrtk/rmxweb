import abc
from functools import update_wrapper
import time

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import requests

from rmxweb.config import (
    PROMETHEUS_JOB, PROMETHEUS_URL, PUSHGATEWAY_HOST, PUSHGATEWAY_PORT,
    SECONDS_AFTER_LAST_CALL
)

CREATE_DATA_PREFIX = "create_data"
COMPUTE_MATRIX_PREFIX = "compute_matrix"
COMPUTE_DENDROGRAM_PREFIX = "compute_dendrogram"

LAST_CALL = 'last_call'
SUCCESS = 'success'
EXCEPTION = 'exception'
DURATION = 'time'
ACTIVE_PROC = 'active_proc'

PROG_PREFIXES = [
    # this is called when a the function to create Data Objects is called by
    # the scraper, the crawler.
    CREATE_DATA_PREFIX,  # - create_from_webpage

    # this is called when the dendrogram is being computed
    COMPUTE_DENDROGRAM_PREFIX,  # - dendrogram

    # this is the prefix for the tasks computing network graphs
    COMPUTE_MATRIX_PREFIX,  # - compute_matrix
]


class BasePrometheus(abc.ABC):

    def __init__(self, *args, dtype: str = None, **kwds):

        self.dtype = dtype
        if self.dtype not in PROG_PREFIXES:
            raise ValueError(f'"{dtype}" is not in {PROG_PREFIXES}')

        self.containerid = None
        self.features = None
        self.func_name = None

    @property
    def gname_suffix(self):
        suffix = f'_containerid_{self.containerid}'
        if self.features is not None:
            suffix += f'_features_{self.features}'
        return suffix

    @property
    def progress_name(self):
        return f'{self.dtype}__{DURATION}_{self.gname_suffix}'

    @property
    def lastcall_name(self):
        return f'{self.dtype}__{LAST_CALL}_{self.gname_suffix}'

    @property
    def exception_name(self):
        return f'{self.dtype}__{EXCEPTION}_{self.gname_suffix}'

    @property
    def success_name(self):
        return f'{self.dtype}__{SUCCESS}_{self.gname_suffix}'


class TrackProgress(BasePrometheus):

    def __init__(self, dtype: str = None):
        super(TrackProgress, self).__init__(dtype=dtype)
        self.registry = None

    def __call__(self, func):

        self.func_name = func.__name__
        update_wrapper(self, func)

        def wrapper(*args, **kwds):
            self.process_parameters(**kwds)
            return self.run(func, *args, **kwds)
        return wrapper

    def process_parameters(self, **kwds):
        if "containerid" in kwds:
            self.containerid = kwds.get('containerid')
        elif "container" in kwds:
            self.containerid = kwds["container"].pk
        self.features = kwds.get('features') or kwds.get('feats')

    def run(self, func, *args, **kwds):
        self.registry = CollectorRegistry()
        try:
            gtime = Gauge(
                self.progress_name,
                f'the progress of {self.dtype}',
                registry=self.registry
            )
            with gtime.time():
                out = func(*args, **kwds)
            gsuccess = Gauge(
                self.success_name,
                f'time of success return on {self.dtype}',
                registry=self.registry
            )
            gsuccess.set(time.time())
            # gsuccess.set_to_current_time()
        except Exception as _:
            gexcept = Gauge(
                self.exception_name,
                f'time of exception on {self.dtype}',
                registry=self.registry
            )
            gexcept.set(time.time())
            # gexcept.set_to_current_time()
            out = None
        finally:
            last = Gauge(
                self.lastcall_name,
                f'time of the last call made to {self.dtype}',
                registry=self.registry
            )
            last.set(time.time())
            # last.set_to_current_time()
            self.push()
        return out

    def push(self):
        push_to_gateway(
            f'{PUSHGATEWAY_HOST}:{PUSHGATEWAY_PORT}',
            job=PROMETHEUS_JOB,
            registry=self.registry
        )


track_progress = TrackProgress


class QueryPrometheus(BasePrometheus):

    time_after_last_call = SECONDS_AFTER_LAST_CALL

    def __init__(self, *args, containerid: (int, str) = None, features: int = None, **kwds):
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
        """This method checks if a record exists in prom and if it was created
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
            # return self.last_call_exception()
        last_call_val = float(last_call_rec['value'][1])
        if time.time() - self.time_after_last_call > last_call_val:
            self.ready = True
        return self.response()

    def check_last_call_exists(self):
        """This method checks if the records exists in prom."""
        exception = self.last_call_exception()
        if exception:
            value = float(exception['value'][1])
            return self.exception_response(value=value)
        if not self.result:
            self.ready = True
            return self.no_results_response()
        return self.response()

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
