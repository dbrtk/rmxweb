

import typing

from rmxweb.celery import celery
from rmxweb.config import NLP_TASKS, RMXGREP_TASK


def get_features(containerid: (int, str), feats: int, path: str):
    """

    :param containerid:
    :param feats:
    :param path:
    :return:
    """
    return celery.send_task(
        NLP_TASKS['retrieve_features'],
        kwargs={'containerid': containerid, 'feats': feats, 'path': path}
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


def hierarchical_tree(containerid: (int, str) = None, feats: int = None,
                      flat: bool = False) -> dict:
    """
    :param containerid:
    :param feats:
    :param path:
    :param flat:
    :return:
    """
    return celery.send_task(NLP_TASKS['hierarchical_tree'], kwargs={
        'containerid': containerid,
        'feats': feats,
        'flat': flat
    }).get()
