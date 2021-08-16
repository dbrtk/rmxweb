"""Emitting miscellaneous messages to the world (other services) through
   celery/rabbitmq.
"""
import os


from prom.config import COMPUTE_MATRIX_PREFIX, CREATE_DATA_PREFIX
from prom.decorator import trackprogress
from rmxweb.celery import celery
from rmxweb.config import (
    CRAWL_START_MONITOR_COUNTDOWN, NLP_TASKS, SCRASYNC_TASKS, RMXWEB_TASKS
)


def get_available_features(containerid: int = None, folder_path: str = None):
    """Retrieves available features from nlp"""
    return celery.send_task(
        NLP_TASKS['available_features'],
        kwargs={'corpusid': containerid, 'path': folder_path}).get()


def crawl_async(url_list: list = None, containerid=None, depth=1):
    """Starting the crawler in scrasync. Starting the task that will monitor
       the crawler.
    """
    crawlid = celery.send_task(SCRASYNC_TASKS['launch_crawl'], kwargs={
        'endpoint': url_list,
        'containerid': containerid,
        'depth': depth
    }).get()
    # the countdown argument is here to make sure that this task does not
    # start immediately as prometheus may be empty.
    celery.send_task(
        RMXWEB_TASKS['monitor_crawl'],
        kwargs={'containerid': containerid, 'crawlid': crawlid},
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


@trackprogress(dtype=COMPUTE_MATRIX_PREFIX)
def generate_matrices_remote(
        container=None,
        feats: int = 10,
        words: int = 6,
        vectors_path: str = None,
        docs_per_feat: int = 0,
        feats_per_doc: int = 3):
    """
    Generating matrices on the remote server.

    :param self:
    :param container: instance of Container
    :param feats:
    :param words:
    :param vectors_path:
    :param docs_per_feat:
    :param feats_per_doc:
    :return:
    """
    containerid = container.pk
    print(f'\n\n\ncalled generate_matrices_remote; containerid: {containerid}; features: {feats}.\n\n')

    kwds = {
        'containerid': containerid,
        'feats': int(feats),
        'words': words,
        'docs_per_feat': int(docs_per_feat),
        'feats_per_doc': int(feats_per_doc),
        'path': container.get_folder_path(),
    }
    if os.path.isfile(vectors_path):
        celery.send_task(NLP_TASKS['factorize_matrices'], kwargs=kwds)
    else:
        celery.send_task(NLP_TASKS['compute_matrices'], kwargs=kwds)
