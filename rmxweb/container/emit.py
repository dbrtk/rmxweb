"""Emitting miscellaneous messages to the world (other services) through
   celery/redis.
"""

from metrics.config import CRAWL_RUN_PREFIX
from metrics.decorator import register_metrics
from rmxweb.celery import celery
from rmxweb.config import (
    CRAWL_START_MONITOR_COUNTDOWN,
    NLP_TASKS,
    SCRASYNC_TASKS,
    RMXWEB_TASKS
)


def get_available_features(containerid: int = None, folder_path: str = None):
    """Retrieves available features from nlp"""
    return celery.send_task(
        NLP_TASKS['available_features'],
        kwargs={
            'containerid': containerid,
            'path': folder_path
        }
    ).get()


@register_metrics(CRAWL_RUN_PREFIX)
def crawl_async(url_list: list = None, container=None, depth=1):
    """Starting the crawler in scrasync. Starting the task that will monitor
       the crawler.
    """
    crawlid = celery.send_task(
        SCRASYNC_TASKS['launch_crawl'],
        kwargs={
            'endpoint': url_list,
            'containerid': container.pk,
            'depth': depth
        }
    ).get()
    # the countdown argument is here to make sure that this task does not
    # start immediately as the metrics db may be empty.
    celery.send_task(
        RMXWEB_TASKS['monitor_crawl'],
        kwargs={
            'containerid': container.pk,
            'crawlid': crawlid
        },
        countdown=CRAWL_START_MONITOR_COUNTDOWN
    )
    return crawlid


def get_features(feats: int = 10,
                 words: int = 6,
                 containerid: int = None,
                 path: str = None,
                 docs_per_feat: int = 0,
                 feats_per_doc: int = 3):
    """ Getting the features from nlp. This will call a view method that
        will retrieve or generate the requested data.
    """
    return celery.send_task(
        NLP_TASKS['features_and_docs'], kwargs={
            'path': path,
            'feats': feats,
            'containerid': containerid,
            'words': words,
            'docs_per_feat': docs_per_feat,
            'feats_per_doc': feats_per_doc
        }
    ).get()
