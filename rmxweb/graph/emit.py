

import typing

from container.decorators import feats_available
from rmxweb.celery import celery
from rmxweb.config import NLP_TASKS, RMXGREP_TASK


def get_features(containerid: (int, str), feats: int, words: int, path: str):
    """
    :param containerid:
    :param feats:
    :param words:
    :param path:
    :return:
    """
    # TODO(): DELETE
    return celery.send_task(
        NLP_TASKS['retrieve_features'],
        kwargs={
            'containerid': containerid,
            'feats': feats,
            'path': path,
            'words': words
        }
    ).get()


def search_texts(words: typing.List[str] = None, highlight: bool = None,
                 path: str = None) -> dict:
    """ Searching a collection of texts for a list of words.
    :param words:
    :param highlight:
    :param path:
    :return:
    """
    return celery.send_task(
        RMXGREP_TASK['search_text'],
        kwargs={
            'highlight': highlight,
            'words': words,
            'container_path': path,
        }).get()


@feats_available
def hierarchical_tree(reqobj: dict) -> dict:
    """
    :param reqobj:
    :return:
    """
    container = reqobj.get('container')
    return celery.send_task(NLP_TASKS['hierarchical_tree'], kwargs={
        'containerid': container.pk,
        'flat': reqobj['flat'],
    }).get(timeout=3)
