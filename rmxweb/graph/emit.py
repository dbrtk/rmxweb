
from rmxweb.celery import celery
from rmxweb.config import NLP_TASKS


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


def search_texts():
    pass


def hierarchical_tree(containerid: (int, str) = None, feats: int = None,
                      path: str = None, flat: bool = False) -> dict:
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
