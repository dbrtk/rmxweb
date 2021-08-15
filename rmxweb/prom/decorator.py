from functools import update_wrapper
import time

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from .base import BasePrometheus
from rmxweb.config import PROMETHEUS_JOB, PUSHGATEWAY_HOST, PUSHGATEWAY_PORT


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
