
from abc import ABC, abstractmethod
from functools import update_wrapper
import time

import prometheus_client as promc
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import requests

from .create_data import CREATE_DATA_PREFIX
from .compute_matrix import COMPUTE_MATRIX_PREFIX
from .dendrogram import COMPUTE_DENDROGRAM_PREFIX

from rmxweb.config import PROMETHEUS_JOB, PUSHGATEWAY_HOST, PUSHGATEWAY_PORT


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


class TrackProgress(ABC):

    def __init__(self, dtype: str = None, label: str = None):

        self.dtype = dtype
        self.label = label

        if self.dtype not in PROG_PREFIXES:
            raise ValueError(f'"{dtype}" is not in {PROG_PREFIXES}')
        self.registry = None
        self.containerid = None
        self.features = None

    def __call__(self, func):

        self.registry = CollectorRegistry()
        update_wrapper(self, func)

        def wrapper(*args, **kwds):
            self.process_parameters(**kwds)
            return self.run(func, *args, **kwds)
        return wrapper

    def process_parameters(self, **kwds):
        self.containerid = kwds.get('containerid')
        self.features = kwds.get('features') or kwds.get('feats')

    def run(self, func, *args, **kwds):
        try:
            gtime = Gauge(
                self.make_progress_name(),
                f'the progress of {self.dtype}',
                registry=self.registry
            )
            with gtime.time():
                out = func(*args, **kwds)
            gsuccess = Gauge(
                self.make_success_name(),
                f'time of success return on {self.dtype}',
                registry=self.registry
            )
            gsuccess.set(time.time())
        except Exception as _:
            gexcept = Gauge(
                self.make_exception_name(),
                f'time of exception on {self.dtype}',
                registry=self.registry
            )
            gexcept.set(time.time())
            out = None
        finally:
            last = Gauge(
                self.make_lastcall_name(),
                f'time of the last call made to {self.dtype}',
                registry=self.registry
            )
            last.set(time.time())
            self.push()
        return out

    @property
    def gname_suffix(self):
        suffix = f'_containerid_{self.containerid}'
        if self.features is not None:
            suffix += f'_features_{self.features}'
        return suffix

    def make_progress_name(self):
        return f'{self.dtype}__{DURATION}_{self.gname_suffix}'

    def make_lastcall_name(self):
        return f'{self.dtype}__{LAST_CALL}_{self.gname_suffix}'

    def make_exception_name(self):
        return f'{self.dtype}__{EXCEPTION}_{self.gname_suffix}'

    def make_success_name(self):
        return f'{self.dtype}__{SUCCESS}_{self.gname_suffix}'

    def push(self):
        push_to_gateway(
            f'{PUSHGATEWAY_HOST}:{PUSHGATEWAY_PORT}',
            job=PROMETHEUS_JOB,
            registry=self.registry
        )
