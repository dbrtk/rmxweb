from rest_framework import serializers

from . import models


class DatasetSerializer(serializers.ModelSerializer):
    """Serializing Data objects when these are displayed as a data_set on the
    level of the Container model/instance.
    """
    class Meta:
        model = models.Data
        fields = ['pk', 'created', 'updated', 'url', 'hostname', 'title',
                  'file_id', 'hash_text', 'container_id']
