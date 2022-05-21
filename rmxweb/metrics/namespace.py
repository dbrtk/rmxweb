
from hashlib import blake2b
import time

from django.db.models import Model

from .config import ENTER, EXIT, PROG_PREFIXES
from .redis import RedisConnect


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
            container = kwds["container"]
            if not isinstance(container, Model):
                raise RuntimeError(
                    f"Expected an instance of a django model. Got {container} "
                    f"instead."
                )
            self.containerid = container.pk
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
        suffix = f"_containerid_{self.containerid}"
        if self.features is not None:
            suffix += f"_features_{self.features}"
        return suffix

    @property
    def enter_name(self):
        msg = f"{self.dtype}__{ENTER}_{self.gname_suffix}"
        return self.hash(msg)

    @property
    def exit_name(self):
        msg = f"{self.dtype}__{EXIT}_{self.gname_suffix}"
        return self.hash(msg)

    @staticmethod
    def hash(message: str = None):
        h = blake2b(digest_size=10)
        h.update(message.encode("utf-8"))
        return h.hexdigest()


class Q(object):
    """Basic methods to query the redis database for metrics."""

    def __init__(self, metrics_names: tuple = None):
        """
        Instantiating the Query object. It takes a list with metrics names that
        will be retrieved from the data store.

        :param metrics_names: list with names of metrics
        :type metrics_names: list
        """
        self.metrics_names = metrics_names
        self.redis = RedisConnect()
        self.result = self.get_metrics()

    def __call__(self):

        pass

    def get_metrics(self):
        """
        Retrieves metrics from redis.

        :return: key value pair with hash names and timestamps
        :rtype: dict
        """
        results = {}
        for key in self.metrics_names:
            value = self.redis.get(key)
            if value:
                results[key] = self.get_timestamp_value(value)
        return results

    def del_record(self, key: str):
        """
        Deletes the record from the database.

        :param key:
        :return:
        """
        self.redis.delete(key)

    @staticmethod
    def record_outdated(timestamp: float):
        """
        Checks if the difference between the timestamp in the record and now is
        greater than 15 minutes.

        :param timestamp:
        :return:
        """
        now = time.time()
        if not isinstance(timestamp, float):
            timestamp = float(timestamp)
        if now - timestamp >= 15 * 60:
            return True
        return False

    @staticmethod
    def get_timestamp_value(value: bytes):
        return float(value.decode("utf-8"))
