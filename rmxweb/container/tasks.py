
import os
from typing import List

from data.models import Data as DataModel
from .models import Container
from prom.config import (
    COMPUTE_MATRIX_RUN_PREFIX,
    CRAWL_CALLBACK_PREFIX,
    INTEGRITY_CHECK_CALLBACK_PREFIX,
    INTEGRITY_CHECK_RUN_PREFIX
)
from prom.decorator import register_with_prom
from rmxweb.config import (
    CRAWL_MONITOR_COUNTDOWN,
    NLP_TASKS,
    RMXWEB_TASKS,
)
from rmxweb.celery import celery


class Error(Exception):
    pass


class __Error(Error):
    pass


@celery.task
@register_with_prom(INTEGRITY_CHECK_RUN_PREFIX)
def integrity_check(containerid: str = None):
    """
    Checks the integrity of the container after the crawler finishes.
    :param containerid:
    :return:
    """
    obj = Container.get_object(pk=containerid)
    celery.send_task(
        NLP_TASKS['integrity_check'],
        kwargs={
            'containerid': containerid,
            'path': obj.get_folder_path(),
        }
    )


@celery.task
@register_with_prom(INTEGRITY_CHECK_CALLBACK_PREFIX, CRAWL_CALLBACK_PREFIX)
def integrity_check_callback(containerid: int = None, path: str = None):
    """
    Task called after the integrity check succeeds on the level of NLP. This
    task is a placeholder for register_with_prom.

    :param containerid: the container id
    :param path: the path
    """
    pass


@celery.task
def delete_data_from_container(
        containerid: str = None, data_ids: List[int] = None):
    """
    :param containerid:
    :param data_ids:
    :return:
    """
    container = Container.get_object(containerid)
    DataModel.delete_many(data_ids=data_ids, containerid=containerid)
    if container.matrix_exists:
        celery.send_task(
            RMXWEB_TASKS['integrity_check'],
            kwargs={'containerid': containerid}
        )


@celery.task
def monitor_crawl(containerid: int = None, crawlid: str = None):
    """This task takes care of the crawl callback.

       The first parameter is empty becasue it is called as a linked task
       receiving a list of endpoints from the scrapper.
    """
    container = Container.get_object(pk=containerid)
    if container.crawl_is_ready():
        # making sure that there is no integrity check in progress
        if container.integrity_check_is_ready():
            celery.send_task(
                RMXWEB_TASKS['integrity_check'],
                kwargs={
                    'containerid': containerid
                }
            )
    else:
        celery.send_task(
            RMXWEB_TASKS['monitor_crawl'],
            kwargs={
                'containerid': containerid
            },
            countdown=CRAWL_MONITOR_COUNTDOWN
        )


@celery.task
def test_task(a: int = None, b: int = None) -> dict:
    """This is a test task."""
    return {
        'sum': a + b
    }


@celery.task
@register_with_prom(COMPUTE_MATRIX_RUN_PREFIX)
def generate_matrix_remote(
        containerid=None,
        features: int = 10,
        words: int = 6,
        docs_per_feat: int = 0,
        feats_per_doc: int = 3):
    """
    Generating matrices on the remote server.

    :param containerid:
    :param features:
    :param words:
    :param docs_per_feat:
    :param feats_per_doc:
    :return:
    """
    container = Container.get_object(pk=containerid)
    kwds = {
        'containerid': containerid,
        'feats': features,
        'words': words,
        'docs_per_feat': int(docs_per_feat),
        'feats_per_doc': int(feats_per_doc),
        'path': container.get_folder_path(),
    }
    if os.path.isfile(container.get_vectors_path()):
        celery.send_task(NLP_TASKS['factorize_matrices'], kwargs=kwds)
    else:
        celery.send_task(NLP_TASKS['compute_matrices'], kwargs=kwds)
