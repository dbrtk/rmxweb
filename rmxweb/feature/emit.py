"""
Functions calling other services
"""

from container.decorators import feats_available
from rmxweb.celery import celery
from rmxweb.config import NLP_TASKS


@feats_available
def get_features(containerid: int = None, container=None, feats: int = None,
                 words: int = None, **_):
    """
    :param containerid:
    :param container:
    :param feats:
    :param words:
    :return:
    """
    resp = celery.send_task(
        NLP_TASKS['retrieve_features'],
        kwargs={
            'containerid': containerid,
            'feats': feats,
            'path': container.get_folder_path(),
            'words': words
        }
    ).get()
    if resp:
        return {'success': True, 'data': resp}
    else:
        return {
            'success': False,
            'msg': f'no features for feature number {feats}'
        }
