"""Metrics factory."""


class MetricsFactory:
    """Metrics Factory registers all metrics classes that are available.
    """
    metrics = {}

    @classmethod
    def set_metrics_cls(cls, metrics_name: str):
        """This is a decorator that, for a given metrics name, registers a
        metrics class.
        :param metrics_name:
        :return:
        """

        def wrapper(metrics_cls):
            """Wrapper around the metrics class."""
            if metrics_name not in cls.metrics:
                cls.metrics[metrics_name] = metrics_cls
            else:
                pass
            return metrics_cls

        return wrapper

    @classmethod
    def get_metrics(cls, metrics_name: str):
        """
        Returns a metrics class for a given metrics class name.
        :param metrics_name:
        :return:
        """
        if metrics_name not in cls.metrics:
            raise ValueError(
                f'{metrics_name} is not defined in available metrics'
            )
        return cls.metrics[metrics_name]
