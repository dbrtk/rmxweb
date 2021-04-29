
from rest_framework import serializers

from . import models


class ContainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Container
        fields = ['name', 'crawl_ready', 'integrity_check_in_progress',
                  'container_ready']


class CrawlStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CrawlStatus
        fields = ['type', 'busy', 'feats', 'task_name', 'task_id', 'container']

