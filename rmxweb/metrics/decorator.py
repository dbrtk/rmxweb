
from functools import wraps
import time

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from .namespace import Namespace
from .redis import RedisConnect
from rmxweb.config import PROMETHEUS_JOB, PUSHGATEWAY_HOST, PUSHGATEWAY_PORT


def register_with_prom(*dtype):
    """
    Decorator to register function and task metrics in prometheus.

    :param dtype:
    :return:
    """
    def inner(func):

        @wraps(func)
        def wrapped(*args, **kwds):
            """
            The wrapper for the decorated function.

            :param args: arguments to be passed to the decorated function
            :param kwds: keyword arguments to be passed to the decorated
             function
            :return: the output returned by the function
            """
            registry = CollectorRegistry()
            namespace = []

            redis_db = RedisConnect()

            for item in dtype:
                base = Namespace(dtype=item)
                base.process_parameters(**kwds)
                namespace.append(base)
                redis_db.set(base.enter_name, time.time())
                # todo(): delete this!
                # genter = Gauge(
                #     base.enter_name,
                #     f"Entering {func.__name__} with dtype: {dtype}",
                #     registry=registry
                # )
                # genter.set(time.time())
            out = func(*args, **kwds)
            for base in namespace:
                redis_db.set(base.exit_name, time.time())
                # todo(): delete this!
                # gexit = Gauge(
                #     base.exit_name,
                #     f"Exiting {func.__name__} with dtype: {dtype}",
                #     registry=registry
                # )
                # gexit.set(time.time())
            # todo(): delete this:
            # push_to_gateway(
            #     f'{PUSHGATEWAY_HOST}:{PUSHGATEWAY_PORT}',
            #     job=PROMETHEUS_JOB,
            #     registry=registry
            # )
            return out
        return wrapped
    return inner
