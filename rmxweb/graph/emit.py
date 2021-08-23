
import typing

from container.decorators import feats_available
from rmxweb.celery import celery
from rmxweb.config import NLP_TASKS, RMXGREP_TASK, RMXWEB_TASKS


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
def hierarchical_tree(containerid=None, flat: bool = None, **_) -> dict:
    """
    :param containerid:
    :param container:
    :param flat:
    :return:
    """
    return celery.send_task(NLP_TASKS['hierarchical_tree'], kwargs={
        'containerid': containerid,
        'flat': flat,
    }).get(timeout=3)
