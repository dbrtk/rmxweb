
from functools import wraps

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import requests

from rmxweb.config import (
    PROMETHEUS_HOST, PROMETHEUS_JOB, PROMETHEUS_PORT, PUSHGATEWAY_HOST,
    PUSHGATEWAY_PORT
)

PROG_PREFIXES = [

    # this is called when the dendrogram is being computed
    'dendrogram',
]
ACTIVE_PROC = 'active_proc'


def make_active_processes_name(dtype: str, containerid: str):

    return f'{dtype}__{ACTIVE_PROC}_{containerid}'


class Incremental:

    def __init__(self, containerid: (int, str), dtype: str, label: str = None):
        """
        :param containerid:
        :param dtype:
        :param label:
        """
        if dtype not in PROG_PREFIXES:
            raise ValueError(f'"{dtype}" is not in {PROG_PREFIXES}')
        self.registry = CollectorRegistry()
        self.g_name = make_active_processes_name(dtype, containerid)
        self.g = self.gauge()
        self.v = self.get_value()

    def gauge(self):
        return Gauge(
            self.g_name,
            'Number of active processes for a task, function.',
            registry=self.registry
        )

    @property
    def endpoint(self):
        return f'http://{PROMETHEUS_HOST}:{PROMETHEUS_PORT}/api/v1/query?' \
               f'query={{__name__=~"{self.g_name}",job="{PROMETHEUS_JOB}"}}'

    def get_metrics(self):
        resp = requests.get(self.endpoint)
        if not resp.ok:
            raise RuntimeError(resp.text)
        return resp.json()

    def get_value(self):
        resp = self.get_metrics()
        try:
            v = next(
                _ for _ in resp['data']['result']
                if _['metric']['__name__'] == self.g_name
            )
            return int(v['value'][1])
        except StopIteration as _:
            return 0

    def inc(self, n: int = 1):
        """Increment gauge's the value by n."""
        self.g.set(self.v + n)
        self.push()

    def dec(self, n: int = 1):
        """Decrement gauge's the value by n."""
        self.g.set(self.v - n)
        self.push()

    def push(self):
        push_to_gateway(
            f'{PUSHGATEWAY_HOST}:{PUSHGATEWAY_PORT}',
            job=PROMETHEUS_JOB,
            registry=self.registry
        )


def increment(dtype: str = None, label: str = None):
    """
    :param dtype:
    :param label:
    :return:
    """
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwds):
            containerid = kwds.get('containerid')
            inst = Incremental(dtype=dtype, containerid=containerid)
            inst.inc()
            return func(*args, **kwds)
        return wrapper
    return inner


def decrement(dtype: str = None, label: str = None):

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwds):
            containerid = kwds.get('containerid')
            inst = Incremental(dtype=dtype, containerid=containerid)
            inst.dec()
            return func(*args, **kwds)
        return wrapper
    return inner


def depprecated_increment(dtype: str = None, label: str = None):
    """
    :param dtype:
    :param label:
    :return:
    """
    # todo(): delete this
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwds):
            containerid = kwds.get('containerid')

            Incremental(dtype=dtype, containerid=containerid)

            if dtype not in PROG_PREFIXES:
                raise ValueError(f'"{dtype}" is not in {PROG_PREFIXES}')
            registry = CollectorRegistry()
            g_name = make_active_processes_name(dtype, containerid)
            g = Gauge(
                g_name,
                'Number of active processes for a task, function.',
                registry=registry
            )
            endpoint = f'http://{PROMETHEUS_HOST}:{PROMETHEUS_PORT}/api/v1/query?query={{__name__=~"{g_name}",job="{PROMETHEUS_JOB}"}}'
            resp = requests.get(endpoint)
            if not resp.ok:
                raise RuntimeError(resp.text)
            resp = resp.json()
            try:
                v = next(_ for _ in resp['data']['result'] if _['metric']['__name__'] == g_name)
                v = int(v['value'][1])
            except StopIteration as _:
                v = 0
            g.set(v + 1)
            g.set_to_current_time()
            push_to_gateway(f'{PUSHGATEWAY_HOST}:{PUSHGATEWAY_PORT}', job=PROMETHEUS_JOB, registry=registry)
            return func(*args, **kwds)
        return wrapper
    return inner
