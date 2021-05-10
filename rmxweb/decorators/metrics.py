

from functools import wraps
import time

import prometheus_client as promc

from rmxweb.config import PROMETHEUS_JOB, PUSHGATEWAY_HOST, PUSHGATEWAY_PORT


CREATE_DOC_PROG_PREFIX = 'create_from_webpage'

LAST_CALL = 'lastcall'
SUCCESS = 'succes'
EXCEPTION = 'exception'
DURATION = 'time'


def make_progress_name(dtype: str = None, containerid: str = None):

    return f'{dtype}__{DURATION}_{containerid}'


def make_lastcall_name(dtype: str = None, containerid: str = None):

    return f'{dtype}__{LAST_CALL}_{containerid}'


def make_exception_name(dtype: str = None, containerid: str = None):

    return f'{dtype}__{EXCEPTION}_{containerid}'


def make_success_name(dtype: str = None, containerid: str = None):

    return f'{dtype}__{SUCCESS}_{containerid}'


def trackprogress(dtype: str = None):

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwds):

            assert dtype in [CREATE_DOC_PROG_PREFIX]
            registry = promc.CollectorRegistry()
            containerid = kwds.get('containerid')

            print(
                f'inside the wrapper. containerid: {containerid}; dtype: {dtype}',
                flush=True
            )
            try:
                gtime = promc.Gauge(
                    make_progress_name(dtype, containerid),
                    f'the progress of {dtype}',
                    registry=registry
                )
                with gtime.time():
                    out = func(*args, **kwds)

                gsuccess = promc.Gauge(
                    make_success_name(dtype, containerid),
                    f'time of success return on {dtype}',
                    registry=registry
                )
                gsuccess.set(time.time())
            except Exception as _:
                gexcept = promc.Gauge(
                    make_exception_name(dtype, containerid),
                    f'time of exception on {dtype}',
                    registry=registry
                )
                gexcept.set(time.time())
                out = None
            finally:
                last = promc.Gauge(
                    make_lastcall_name(dtype, containerid),
                    f'time of the last call made to {dtype}',
                    registry=registry
                )
                last.set(time.time())

                promc.push_to_gateway(
                    f'{PUSHGATEWAY_HOST}:{PUSHGATEWAY_PORT}',
                    job=PROMETHEUS_JOB,
                    registry=registry
                )
            return out
        return wrapper
    return inner
