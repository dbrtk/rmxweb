
from functools import wraps

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import requests

from .config import PROG_PREFIXES
from rmxweb.config import (
    PROMETHEUS_HOST, PROMETHEUS_JOB, PROMETHEUS_PORT, PUSHGATEWAY_HOST,
    PUSHGATEWAY_PORT
)

ACTIVE_PROC = 'running_process'


def make_active_processes_name(dtype: str, containerid: str):

    return f'{dtype}__{ACTIVE_PROC}_{containerid}'


class Incremental:
    """
    These are incremental metrics, like the number of requests made to a
    service. The value is incremented when the endpoint is called and
    decremented when it finishes processing and returns a value.
    """
    def __init__(self, containerid: (int, str), dtype: str, label: str = None, args: list = None, kwds: dict = None):
        """
        :param containerid:
        :param dtype:
        :param label:
        """
        if dtype not in PROG_PREFIXES:
            raise ValueError(f'"{dtype}" is not in {PROG_PREFIXES}')
        self.registry = CollectorRegistry()
        self.params = []
        self.g_name = make_active_processes_name(dtype, containerid)
        print(f'The Gauge`s name: {self.g_name}')
        self.g = self.gauge()
        self.v = self.get_value()
        print(f'The Gauge after instantiation: {self.g}; the gauge`s value: {self.g}')
        self.inc()
        print(f'th gauge value after inc: {self.get_value()}')
        print(f'the value as queried from prom: {self.query_value()}')

    def gauge(self):
        return Gauge(
            self.g_name,
            'Number of active processes for a task, function.',
            registry=self.registry
        )

    def process_kwds(self, kwds: dict):
        feats = kwds.get('feats') or kwds.get('features')
        containerid = kwds.get('containerid')
        self.params.append(('containerid', containerid))
        if feats is not None:
            self.params.append(('feats', feats))

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
        """Retrieve gauge's value."""
        try:
            metric = next(_ for _ in self.g.collect() if _.name == self.g_name)
            print(f'GET_VALUE --------> The metric samples: length: {len(metric.samples)} objects: {metric.samples}')
            sample = next(_ for _ in metric.samples if _.name == self.g_name)
        except StopIteration as err:
            return
        return sample.value

    def query_value(self):
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
        print(f'\nThe gauge name while  incrementing: {self.g_name}; the current value: {self.v}.\n')
        # self.g.set(self.v + n)
        self.g.inc(1)
        self.push()

    def dec(self, n: int = 1):
        """Decrement gauge's the value by n."""
        print(f'\nThe gauge name while  decrementing: {self.g_name}; the current value: {self.v}.\n')
        # self.g.set(self.v - n)
        self.g.dec(1)
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
            print(f'\n\ninside the increment decorator with kwds: {kwds}\n\n')
            inst = Incremental(dtype=dtype, containerid=containerid)
            print(f'INCREMENT -----> the gauge name on the instance: {inst.g_name}\n')
            inst.inc()
            return func(*args, **kwds)
        return wrapper
    return inner


def decrement(dtype: str = None, label: str = None):
    """
    :param dtype:
    :param label:
    :return:
    """
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwds):
            containerid = kwds.get('containerid')
            print(f'\n\ninside the decrement decorator with kwds: {kwds}\n\n')
            inst = Incremental(dtype=dtype, containerid=containerid)
            print(f'DECREMENT ----> the gauge name on the instance: {inst.g_name}\n')
            inst.dec()
            return func(*args, **kwds)
        return wrapper
    return inner
