
import os
import time
from typing import List

from data.models import Data as DataModel
from prom.track_progress import (
    COMPUTE_MATRIX_PREFIX, CREATE_DATA_PREFIX, track_progress
)


from .models import Container, FeaturesStatus
from rmxweb.config import (
    CRAWL_MONITOR_COUNTDOWN, CRAWL_START_MONITOR_COUNTDOWN, NLP_TASKS,
    PROMETHEUS_JOB, PROMETHEUS_URL, RMXWEB_TASKS, SCRASYNC_TASKS,
    SECONDS_AFTER_LAST_CALL
)
import requests
from rmxweb.celery import celery


class Error(Exception):
    pass


class __Error(Error):
    pass


# def dec(func):
#     # todo(): delete - this is a test decorator
#     def wrapper(*args, **kwds):
#
#         print('\n\n\nDCEORATOR')
#         print(f"exec decorated function: {func.__name__}")
#         print(f"args: {args}; kwds: {kwds}")
#         return func(*args, **kwds)
#     return wrapper


@track_progress(dtype=COMPUTE_MATRIX_PREFIX)
@celery.task
def generate_matrices_remote(
        containerid: str = None,
        feats: int = 10,
        words: int = 6,
        vectors_path: str = None,
        docs_per_feat: int = 0,
        feats_per_doc: int = 3):
    """
    Generating matrices on the remote server.

    :param self:
    :param containerid:
    :param feats:
    :param words:
    :param vectors_path:
    :param docs_per_feat:
    :param feats_per_doc:
    :return:
    """
    # todo(): delete!
    print(f'\n\n\ncalled generate_matrices_remote; containerid: {containerid}; features: {feats}.\n\n')
    container = Container.get_object(pk=containerid)
    FeaturesStatus.set_status_feats(
        containerid=container.pk,
        busy=True,
        feats=feats,
    )
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


@track_progress(dtype=COMPUTE_MATRIX_PREFIX)
def _nlp_callback_success(**kwds):
    """
    Called when NLp finishes computing the graphs, all the necessary objects.
    """
    print(f"Called NLP callback success. kwds: {kwds}")
    container = Container.get_object(pk=kwds.get('containerid'))
    container.update_on_nlp_callback(feats=kwds.get('feats'))


@celery.task
def nlp_callback_success(**kwds):
    """
    Called when a nlp callback is sent to proximitybot. This task is called by
    the nlp container.
    """
    print(f'\n\n\ncalled nlp_callback_succes; kwds: {kwds}.\n\n')
    _nlp_callback_success(**kwds)

# @celery.task
# def file_extract_callback(kwds: dict = None):
#     """ Called after creating a data object from an uploaded file.
#     # todo(): delete this!
#     :param kwds:
#     :return:
#     """
#     # todo(): delete this task - don't use file upload
#     corpusid = kwds.get('corpusid')
#     data_id = kwds.get('data_id')
#     file_id = kwds.get('file_id')
#     file_name = kwds.get('file_name')
#     success = kwds.get('success')
#     texthash = kwds.get('texthash')
#     if success and data_id:
#         insert_urlobj(
#             corpusid,
#             {
#                 'data_id': data_id,
#                 'file_id': file_id,
#                 'texthash': texthash,
#                 'title': file_name,
#             }
#         )
#     doc = Container.file_extract_callback(
#         containerid=corpusid, unique_file_id=file_id)
#
#     if not doc['expected_files']:
#         if doc.matrix_exists:
#
#             celery.send_task(
#                 RMXWEB_TASKS['integrity_check'],
#                 kwargs={
#                     'containerid': corpusid
#                 }
#             )
#         else:
#             set_crawl_ready(corpusid, True)
#

@celery.task
def integrity_check(containerid: str = None):
    """
    Checks the integrity of the container after the crawler finishes.
    :param containerid:
    :return:
    """
    obj = Container.get_object(pk=containerid)
    obj.set_integrity_check_in_progress()
    celery.send_task(NLP_TASKS['integrity_check'], kwargs={
        'containerid': containerid,
        'path': obj.get_folder_path(),
    })


@celery.task
def integrity_check_callback(containerid: int = None):
    """Task called after the integrity check succeeds on the level of NLP."""
    container = Container.get_object(pk=containerid)
    container.set_integrity_check_ready()


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
# def expected_files(corpusid: str = None, file_objects: list = None):
#     """Updates the container with expected files that are processed."""
#     # todo(): delete this
#     Container.update_expected_files(
#         containerid=corpusid, file_objects=file_objects)
#
#     corpus = Container.get_object(pk=corpusid)
#     return {
#         'corpusid': corpusid,
#         # 'vectors_path': corpus.get_vectors_path(),
#         'corpus_files_path': corpus.texts_path(),
#         # 'matrix_path': corpus.matrix_path,
#         # 'wf_path': corpus.wf_path,
#     }
#
#
# @celery.task
# def create_from_upload(name: str = None, file_objects: list = None):
#     """Creating a container from file upload."""
#     # todo(): delete this
#     docid = str(Container.inst_new_doc(name=name))
#     corpus = Container.get_object(pk=docid)
#     corpus['expected_files'] = file_objects
#     corpus['data_from_files'] = True
#
#     # todo(): set status to busy
#     corpus.save()
#
#     return {
#         'corpusid': docid,
#         # 'corpus_path': corpus.get_corpus_path(),
#         'corpus_files_path': corpus.texts_path()
#     }


@celery.task
def process_crawl_resp(resp, containerid, crawlid):
    """
    Processing the response of the crawler. This task checks if the crawl is
    ready and if it finished. If yes, the integrity_check is called.

    This task processes the response form crawl_metrics.
    :param resp:
    :param containerid:
    :return:
    """
    crawl_status = Container.container_status(containerid)
    if resp.get('ready'):
        celery.send_task(
            SCRASYNC_TASKS['delete_crawl_status'],
            kwargs={'containerid': containerid, 'crawlid': crawlid}
        )
        container = Container.get_object(pk=containerid)
        container.set_crawl_ready(value=True)
        if not crawl_status['integrity_check_in_progress']:
            celery.send_task(
                RMXWEB_TASKS['integrity_check'],
                kwargs={'containerid': containerid}
            )
    else:
        celery.send_task(
            RMXWEB_TASKS['monitor_crawl'],
            args=[containerid],
            countdown=CRAWL_MONITOR_COUNTDOWN
        )


@celery.task
def monitor_crawl(containerid: int = None, crawlid: str = None):
    """This task takes care of the crawl callback.

       The first parameter is empty becasue it is called as a linked task
       receiving a list of endpoints from the scrapper.
    """
    celery.send_task(
        RMXWEB_TASKS['crawl_metrics'],
        kwargs={'containerid': containerid},
        link=process_crawl_resp.s(containerid, crawlid)
    )


# todo(): delete this should be in prom
@celery.task
def crawl_metrics(containerid: int = None):
    """
    Querying all metrics for scrasync
    the response = {
        'status': 'success',
        'data': {
            'resultType': 'vector',
            'result': [{
                'metric': {
                    '__name__': 'create_from_webpage__lastcall_<containerid>',
                    'job': 'scrasync'
                },
                'value': [1613125321.823, '1613125299.354587']
            }, {
                'metric': {
                    '__name__': 'create_from_webpage__succes_<containerid>',
                    'job': 'scrasync'
                }, 'value': [1613125321.823, '1613125299.3545368']
            }]
        }
    }
    """
    ready = False

    exception = f'{CREATE_DATA_PREFIX}__exception_{containerid}'
    success = f'{CREATE_DATA_PREFIX}__succes_{containerid}'
    lastcall = f'{CREATE_DATA_PREFIX}__lastcall_{containerid}'
    query = '{{__name__=~"{success}|{lastcall}|{exception}",job="{job}"}}'\
        .format(
            success=success,
            exception=exception,
            lastcall=lastcall,
            job=PROMETHEUS_JOB
        )
    endpoint = f'http://{PROMETHEUS_URL}/query?query={query}'
    del_endpoint = 'http://{}/admin/tsdb/delete_series?match={}'.format(
        PROMETHEUS_URL, query
    )
    resp = requests.get(endpoint)
    resp = resp.json()
    result = resp.get('data', {}).get('result', [])
    if not result:
        # This is returned when there are no results; the crawl is finished
        # and the container is ready.
        return {
            'ready': True,
            'result': result,
            'msg': 'no records in prometheus',
            'containerid': containerid
        }
    lastcall_obj = next(
        _ for _ in result
        if _.get('metric').get('__name__') == lastcall
    )
    lastcall_val = float(lastcall_obj['value'][1])
    if time.time() - SECONDS_AFTER_LAST_CALL > lastcall_val:
        ready = True
        # resp = requests.post(del_endpoint)
    return {
        'containerid': containerid,
        'ready': ready,
        'msg': 'crawl ready',
        'result': result
    }


@celery.task
def test_task(a: int = None, b: int = None) -> dict:
    """This is a test task."""
    return {
        'sum': a + b
    }
