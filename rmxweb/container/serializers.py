
from rest_framework import serializers

from . import models


class ContainerSerializer(serializers.HyperlinkedModelSerializer):

    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()

    class Meta:
        model = models.Container
        fields = ['name', 'crawl_ready', 'integrity_check_in_progress']


class CrawlStatusSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.CrawlStatus
        fields = ['type', 'busy', 'feats', 'task_name', 'task_id', 'container']

