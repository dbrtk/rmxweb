""" Models for the Data Objects. """

from django.core.validators import URLValidator
from django.db import models

from ..container.models import Container


class Data(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    container = models.ForeignKey(Container, on_delete=models.CASCADE)

    hostname = models.CharField(max_length=300)
    url = models.TextField(validators=[URLValidator])

