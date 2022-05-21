
import typing

from container.decorators import feats_available
from metrics.config import COMPUTE_DENDROGRAM_RUN_PREFIX
from metrics.decorator import register_metrics
from metrics.dendrogram import DendrogramReady
from rmxweb.celery import celery
from rmxweb.config import NLP_TASKS, RMXGREP_TASK


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


@register_metrics(COMPUTE_DENDROGRAM_RUN_PREFIX)
def compute_dendrogram(containerid: int = None):
    """
    Computing the dendrogram for a given containerid.

    :param containerid:
    """
    celery.send_task(
        NLP_TASKS['compute_dendrogram'],
        kwargs={
            'containerid': containerid
        }
    )


@feats_available
def hierarchical_tree(containerid: int = None, flat: bool = None, **_) -> dict:
    """
    :param containerid:
    :param container:
    :param flat:
    :return:
    """
    resp = celery.send_task(
        NLP_TASKS['hierarchical_tree'],
        kwargs={
            'containerid': containerid,
            'flat': flat,
        }
    ).get(timeout=3)
    if resp.get("success"):
        return resp

    # check whether nlp is runnning the same process
    stats = DendrogramReady(containerid=containerid)()
    if not stats.get("ready", False):
        return {"success": False, "busy": True, "payload": stats}

    compute_dendrogram(containerid=containerid)
    return {"success": False, "busy": True}
