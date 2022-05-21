
from functools import wraps
import time

from .namespace import Namespace
from .redis import RedisConnect


def register_with_prom(*dtype):
    """
    Decorator to register function and task in metrics that are saved in redis.

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
            namespace = []
            redis_db = RedisConnect()

            for item in dtype:
                base = Namespace(dtype=item)
                base.process_parameters(**kwds)
                namespace.append(base)
                redis_db.set(base.enter_name, time.time())
            out = func(*args, **kwds)
            for base in namespace:
                redis_db.set(base.exit_name, time.time())
            return out
        return wrapped
    return inner
