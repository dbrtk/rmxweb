""" Models for the container that holds data related to specific crawls.
"""

from django.core.validators import URLValidator
from django.db import models


class Container(models.Model):

    name = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    crawl_ready = models.BooleanField(default=False)
    integrity_check_in_progress = models.BooleanField(default=False)


class Url(models.Model):

    url = models.TextField(validators=[URLValidator])
    created = models.DateTimeField(auto_now_add=True)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)


class CrawlStatus(models.Model):

    type = models.CharField(max_length=100)
    busy = models.BooleanField(default=False)
    feats = models.IntegerField()
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(max_length=100)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)

