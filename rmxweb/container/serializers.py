
from rest_framework import serializers

from . import models


class ContainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Container
        fields = [
            'pk',
            'name',
            'created',
            'updated',
            'uid'
        ]
