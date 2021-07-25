
from functools import wraps
import time

import prometheus_client as promc
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import requests

from rmxweb.config import (PROMETHEUS_HOST, PROMETHEUS_JOB, PROMETHEUS_PORT, PUSHGATEWAY_HOST, PUSHGATEWAY_PORT)

# todo(): delete this (CREATE_DOC_PROG_PREFIX)
CREATE_DOC_PROG_PREFIX = 'create_from_webpage'

PROG_PREFIXES = [
    # this is called when a the function to create Data Objects is called by
    # the scraper, the crawler.
    'create_from_webpage',

    # this is called when the dendrogram is being computed
    'dendrogram',
]

LAST_CALL = 'last_call'
SUCCESS = 'success'
EXCEPTION = 'exception'
DURATION = 'time'
ACTIVE_PROC = 'active_proc'


def make_progress_name(dtype: str = None, containerid: str = None):

    return f'{dtype}__{DURATION}_{containerid}'


def make_lastcall_name(dtype: str = None, containerid: str = None):

    return f'{dtype}__{LAST_CALL}_{containerid}'


def make_exception_name(dtype: str = None, containerid: str = None):

    return f'{dtype}__{EXCEPTION}_{containerid}'


def make_success_name(dtype: str = None, containerid: str = None):

    return f'{dtype}__{SUCCESS}_{containerid}'



def trackprogress(dtype: str = None):
    """ Decorator that tracks the progress of functions. It assumes that the
    call to the function contains a `containerid` parameter.

    :param dtype: the prefix for the name of the metric
    :return:
    """
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwds):

            if dtype not in PROG_PREFIXES:
                raise ValueError(f'"{dtype}" is not in {PROG_PREFIXES}')
            registry = CollectorRegistry()
            containerid = kwds.get('containerid')

            # print(
            #     f'inside the wrapper. containerid: {containerid}; dtype: {dtype}',
            #     flush=True
            # )
            try:
                gtime = Gauge(
                    make_progress_name(dtype, containerid),
                    f'the progress of {dtype}',
                    registry=registry
                )
                with gtime.time():
                    out = func(*args, **kwds)

                gsuccess = Gauge(
                    make_success_name(dtype, containerid),
                    f'time of success return on {dtype}',
                    registry=registry
                )
                gsuccess.set(time.time())
            except Exception as _:
                gexcept = Gauge(
                    make_exception_name(dtype, containerid),
                    f'time of exception on {dtype}',
                    registry=registry
                )
                gexcept.set(time.time())
                out = None
            finally:
                last = Gauge(
                    make_lastcall_name(dtype, containerid),
                    f'time of the last call made to {dtype}',
                    registry=registry
                )
                last.set(time.time())

                push_to_gateway(
                    f'{PUSHGATEWAY_HOST}:{PUSHGATEWAY_PORT}',
                    job=PROMETHEUS_JOB,
                    registry=registry
                )
            return out
        return wrapper
    return inner
