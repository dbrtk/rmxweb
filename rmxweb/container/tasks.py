
import time
from typing import List

import requests

from data.models import Data as DataModel
from .models import Container
from prom.config import COMPUTE_MATRIX_PREFIX, CREATE_DATA_PREFIX
from prom.decorator import track_progress, trackprogress
from rmxweb.config import (
    CRAWL_MONITOR_COUNTDOWN, CRAWL_START_MONITOR_COUNTDOWN, NLP_TASKS,
    PROMETHEUS_JOB, PROMETHEUS_URL, RMXWEB_TASKS, SCRASYNC_TASKS,
    SECONDS_AFTER_LAST_CALL
)
from rmxweb.celery import celery


class Error(Exception):
    pass


class __Error(Error):
    pass


@celery.task
@trackprogress(dtype=COMPUTE_MATRIX_PREFIX)
def nlp_callback_success(**kwds):
    """
    Called when a nlp callback is sent to proximitybot. This task is called by
    the nlp container.
    """
    print(f'\n\n\ncalled nlp_callback_succes; kwds: {kwds}.\n\n')
    container = Container.get_object(pk=kwds.get('containerid'))
    container.update_on_nlp_callback(feats=kwds.get('feats'))


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
