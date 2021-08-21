
import re

import requests

from .config import DURATION, EXCEPTION, LAST_CALL, PROG_PREFIXES, SUCCESS
from rmxweb.config import (
    PROMETHEUS_JOB, PROMETHEUS_URL, SECONDS_AFTER_LAST_CALL
)


class Namespace(object):

    def __init__(
            self,
            *args,
            dtype: str = None,
            **kwds
    ):
        """
        Instantiating the Namespace.

        :param args:
        :param dtype:
        :param kwds:
        """
        if dtype not in PROG_PREFIXES:
            raise ValueError(f'"{dtype}" is not in {PROG_PREFIXES}')
        self.dtype = dtype
        self.containerid = None
        self.features = None
        self.process_parameters(**kwds)
        if any(_ is None for _ in (self.features, self.containerid)):
            raise RuntimeError(f"containerid adn features are required")
        self.func_name = None

    def process_parameters(self, **kwds):
        """
        Process key-word parameters passed to the class to get the container id
        and features number. Possible parameters are:

        * containerid: int
        * container: instance of container.models.Container
        * features: int
        * feats: int

        :param kwds:
        :return:
        """
        if "containerid" in kwds:
            self.containerid = kwds.get("containerid")
        elif "container" in kwds:
            self.containerid = kwds["container"].pk
        if "features" in kwds:
            self.features = kwds.get("features")
        elif "feats" in kwds:
            self.features = kwds.get("feats")

    @property
    def gname_suffix(self):
        """
        Returns the suffix for the name of a record that implements a Gauge.

        :return: suffix for the name of the Gauge
        :rtype: string
        """
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


class Q(object):
    """Basic methods to query prometheus."""

    def __init__(self, metrics_names: tuple = None):
        """
        Instantiating the Query object. It takes a list with metrics names that
        will be retrieved from the data store.

        :param metrics_names: list with names of metrics
        :type metrics_names: list
        """
        self.metrics_names = metrics_names
        self.result = self.get_metrics()

    def __call__(self):

        pass

    def prom_query(self):
        """
        Builds the query that is sent to prometheus in order to retrieve time
        series with metrics.

        :return: the prometheus query to be sent to the server
        :rtype: string
        """
        for item in self.metrics_names:
            if not self.validate_metrics_name(item):
                raise ValueError(f"Wrong metrics name: '{item}'")
        return '{{__name__=~"{metrics}",job="{job}"}}'.format(
            metrics="|".join(self.metrics_names),
            job=PROMETHEUS_JOB
        )

    @staticmethod
    def validate_metrics_name(mn):
        """
        Validating the metrics name.

        :return: True if the name is valid, otherwise False
        :rtype: bool
        """
        return bool(re.match(r"^[A-Za-z0-9-_]*$", mn))

    def get_metrics(self):
        """
        Querying the server that implements prometheus for metrics.

        :return: a list containing records that match the query
        :rtype: list
        """
        q = self.prom_query()
        endpoint = f'http://{PROMETHEUS_URL}/query?query={q}'
        resp = requests.get(endpoint)
        resp = resp.json()
        return resp.get('data', {}).get('result', [])

    def get_record(self, name: str = None):
        """
        Returns a record for a given metrics name.

        :param name: the name of the metrics
        :type name: string
        :return: record
        :rtype: dict
        """
        try:
            return next(
                _ for _ in self.result
                if _.get('metric').get('__name__') == name
            )
        except StopIteration:
            return
