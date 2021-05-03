
from django.db import models

from container.models import Container


class CrawlState(models.Model):

    crawlid = models.CharField(max_length=50, blank=True, null=True)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    url = models.URLField()
    urlid = models.CharField(max_length=300, blank=True, null=True)
    ready = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['url', 'crawlid'],
    #             name='unique_url_for_crawl'
    #         )
    #     ]

    # @classmethod
    # def create(cls, crawlid: str = None, containerid: int = None,
    #            url: str = None, urlid: str = None):
    #     """
    #     :param crawlid:
    #     :param containerid:
    #     :param url:
    #     :param urlid:
    #     :return:
    #     """
    #     # todo(): delete this
    #     container = Container.get_object(containerid)
    #
    #     obj = cls(crawlid=crawlid, container=container, url=url,
    #               urlid=urlid)
    #     obj.save()
    #     return obj

    @classmethod
    def push_many(cls, containerid: int = None, urls: list = None,
                  crawlid: str = None):
        """
        Push many items to the crawl_state collection.
        :param containerid:
        :param urls:
        :param crawlid:
        :return:
        """
        container = Container.get_object(containerid)
        try:
            duplicates = cls.objects.filter(
                crawlid=crawlid, url__in=[_[0] for _ in urls]
            )
        except cls.DoesNotExist:
            duplicates = []
        duplicates = [(_.url, _.urlid) for _ in duplicates]
        urls = list(set(urls).difference(duplicates))
        objs = Container.objects.bulk_create([
            cls(container=container,
                url=url,
                crawlid=crawlid,
                urlid=urlid)
            for url, urlid in urls
        ])
        return objs, duplicates

    @classmethod
    def state_list(cls, crawlid: str = None, containerid: int = None):
        """ For a containerid, retrieve all documents. This shows all active
            processes (scraping, html cleanup, writing to disk).
        """
        container = Container.get_object(containerid)
        try:
            return cls.objects.filter(container=container)
        except cls.DoesNotExist:
            return []

    @classmethod
    def get_saved_endpoints(cls, containerid: int = None):
        """ Returns alist of saved endpoints. """
        return [_.url for _ in cls.state_list(containerid=containerid)]

    @classmethod
    def delete_many(cls, containerid: int = None, crawlid: str = None):
        """
        Deletes many objects from the database.
        :param containerid:
        :param crawlid:
        :return:
        """
        container = Container.get_object(containerid)
        try:
            Container.objects.filter(container=container).delete()
        except cls.DoesNotExist:
            pass
