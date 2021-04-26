
from django.db import models

from container.models import Container


class CrawlState(models.Model):

    crawlid = models.CharField(max_length=50)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    url = models.URLField()
    ready = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, crawlid: str = None, containerid: int = None,
               url: str = None):
        """
        :param crawlid:
        :param containerid:
        :param url:
        :return:
        """
        container = Container.objects.get(pk=containerid)
        if not container:
            return None
        obj = cls(crawlid=crawlid, container=container, url=url)
        obj.save()
        return obj
