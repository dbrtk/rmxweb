import time

from django.db import models

from .namespace import Namespace


# todo(): delete this module!

class Metrics(models.Model):

    ENTER = "EN"
    EXIT = "EX"
    ERROR = "ER"
    STATE_CHOICES = [
        (ENTER, "ENTER"),
        (EXIT, "EXIT"),
        (ERROR, "ERROR"),
    ]
    timestamp = models.DecimalField(
        max_digits=20, decimal_places=10, defualt=time.time()
    )
    containerid = models.CharField(max_length=500, null=False)
    dtype = models.CharField(max_length=500, null=False)
    features = models.IntegerField(null=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=EXIT)

    # todo(): delete the name - replace it with proper columns / db fields
    name = models.CharField(max_length=500, null=False)

    description = models.CharField(max_length=600, null=True)

    def delete_record(self, **kwds):
        """
        Delete enter and exit records for a given containerid, features number.
        :return:
        """
        ns = Namespace(**kwds)

    @classmethod
    def query_params(cls, ns: Namespace):
        q_params = {
            "containerid": ns.containerid,
            "dtype": ns.dtype
        }
        if ns.features:
            q_params["features"] = ns.features
        return q_params

    @classmethod
    def get_record(cls, **kwds):
        ns = Namespace(**kwds)
        cls.objects.get(**cls.query_params(ns))

    def record_outdated(self):

        ...
