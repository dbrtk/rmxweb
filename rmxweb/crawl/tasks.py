
from django.core.serializers import serialize

from rmxweb.celery import celery
from .models import CrawlState


@celery.task
def push_many(containerid: int = None, urls: list = None, crawlid: str = None):
    """
    Push many items to the crawl_state collection.
    It returns a list of inserted objects and a list of duplicates. the latter
    contains tuples of (url, urlid)  -same format as urls.

    :param containerid: integer
    :param urls: list of tuples, each of them containing a url and an urlid.
    :param crawlid: string of a uuid
    :return:
    """
    objs, duplicates = CrawlState.push_many(
        containerid=containerid,
        urls=urls,
        crawlid=crawlid
    )
    return {'objects': serialize('json', objs), 'duplicates': duplicates}


@celery.task
def get_saved_endpoints(containerid: int = None):
    """ Returns alist of saved endpoints. """
    return serialize('json', CrawlState.state_list(containerid=containerid))


@celery.task
def delete_many(containerid: int = None):
    """
    Deletes all objects for a given containerid or crawlid.
    :param containerid:
    :return:
    """
    CrawlState.delete_many(containerid=containerid)
