
import os
from typing import List

from data.models import Data as DataModel
from .models import Container
from prom.config import (
    COMPUTE_MATRIX_RUN_PREFIX,
    CREATE_DATA_PREFIX,
    INTEGRITY_CHECK_CALLBACK_PREFIX,
    INTEGRITY_CHECK_RUN_PREFIX
)
from prom.decorator import track_progress, trackprogress
from rmxweb.config import (
    CRAWL_MONITOR_COUNTDOWN,
    NLP_TASKS,
    PROMETHEUS_JOB,
    PROMETHEUS_URL,
    RMXWEB_TASKS,
    SCRASYNC_TASKS,
    SECONDS_AFTER_LAST_CALL,
)
from rmxweb.celery import celery


class Error(Exception):
    pass


class __Error(Error):
    pass


@celery.task
@trackprogress(dtype=INTEGRITY_CHECK_RUN_PREFIX)
def integrity_check(containerid: str = None):
    """
    Checks the integrity of the container after the crawler finishes.
    :param containerid:
    :return:
    """
    obj = Container.get_object(pk=containerid)
    # todo(): delete this line
    # obj.set_integrity_check_in_progress()
    celery.send_task(
        NLP_TASKS['integrity_check'],
        kwargs={
            'containerid': containerid,
            'path': obj.get_folder_path(),
        }
    )


@celery.task
@trackprogress(dtype=INTEGRITY_CHECK_CALLBACK_PREFIX)
def integrity_check_callback(containerid: int = None, path: str = None):
    """Task called after the integrity check succeeds on the level of NLP."""
    container = Container.get_object(pk=containerid)
    container.toggle_container_ready()
    if not container.container_ready:
        raise RuntimeError(
            f"The container ({container}) should be ready to use."
        )


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


# @celery.task
# def process_crawl_resp(resp, containerid, crawlid):
#     """
#     Processing the response of the crawler. This task checks if the crawl is
#     ready and if it finished. If yes, the integrity_check is called.
#
#     This task processes the response form crawl_metrics.
#     :param resp:
#     :param containerid:
#     :return:
#     """
#     # todo(): delete this task
#     # todo(): delete this task
#     # todo(): delete this task
#     crawl_status = Container.container_status(containerid)
#     if resp.get('ready'):
#         celery.send_task(
#             SCRASYNC_TASKS['delete_crawl_status'],
#             kwargs={'containerid': containerid, 'crawlid': crawlid}
#         )
#         container = Container.get_object(pk=containerid)
#
#         container.set_crawl_ready(value=True)
#         if not crawl_status['integrity_check_in_progress']:
#             celery.send_task(
#                 RMXWEB_TASKS['integrity_check'],
#                 kwargs={'containerid': containerid}
#             )
#     else:
#         celery.send_task(
#             RMXWEB_TASKS['monitor_crawl'],
#             args=[containerid],
#             countdown=CRAWL_MONITOR_COUNTDOWN
#         )


@celery.task
def monitor_crawl(containerid: int = None, crawlid: str = None):
    """This task takes care of the crawl callback.

       The first parameter is empty becasue it is called as a linked task
       receiving a list of endpoints from the scrapper.
    """
    container = Container.get_object(pk=containerid)
    if container.crawl_is_ready() and not container.container_ready:
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


# # todo(): delete this should be in prom
# @celery.task
# def crawl_metrics(containerid: int = None):
#     """
#     Querying all metrics for scrasync
#     the response = {
#         'status': 'success',
#         'data': {
#             'resultType': 'vector',
#             'result': [{
#                 'metric': {
#                     '__name__': 'create_from_webpage__lastcall_<containerid>',
#                     'job': 'scrasync'
#                 },
#                 'value': [1613125321.823, '1613125299.354587']
#             }, {
#                 'metric': {
#                     '__name__': 'create_from_webpage__succes_<containerid>',
#                     'job': 'scrasync'
#                 }, 'value': [1613125321.823, '1613125299.3545368']
#             }]
#         }
#     }
#     """
#     # todo(): delete this
#     # todo(): delete this
#     # todo(): delete this
#     ready = False
#
#     exception = f'{CREATE_DATA_PREFIX}__exception_{containerid}'
#     success = f'{CREATE_DATA_PREFIX}__succes_{containerid}'
#     lastcall = f'{CREATE_DATA_PREFIX}__lastcall_{containerid}'
#     query = '{{__name__=~"{success}|{lastcall}|{exception}",job="{job}"}}'\
#         .format(
#             success=success,
#             exception=exception,
#             lastcall=lastcall,
#             job=PROMETHEUS_JOB
#         )
#     endpoint = f'http://{PROMETHEUS_URL}/query?query={query}'
#     del_endpoint = 'http://{}/admin/tsdb/delete_series?match={}'.format(
#         PROMETHEUS_URL, query
#     )
#     resp = requests.get(endpoint)
#     resp = resp.json()
#     result = resp.get('data', {}).get('result', [])
#     if not result:
#         # This is returned when there are no results; the crawl is finished
#         # and the container is ready.
#         return {
#             'ready': True,
#             'result': result,
#             'msg': 'no records in prometheus',
#             'containerid': containerid
#         }
#     lastcall_obj = next(
#         _ for _ in result
#         if _.get('metric').get('__name__') == lastcall
#     )
#     lastcall_val = float(lastcall_obj['value'][1])
#     if time.time() - SECONDS_AFTER_LAST_CALL > lastcall_val:
#         ready = True
#         # resp = requests.post(del_endpoint)
#     return {
#         'containerid': containerid,
#         'ready': ready,
#         'msg': 'crawl ready',
#         'result': result
#     }


@celery.task
def test_task(a: int = None, b: int = None) -> dict:
    """This is a test task."""
    return {
        'sum': a + b
    }


@celery.task
@trackprogress(dtype=COMPUTE_MATRIX_RUN_PREFIX)
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
