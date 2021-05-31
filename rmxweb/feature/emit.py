"""
Functions calling other services
"""

from container.decorators import feats_available
from rmxweb.celery import celery
from rmxweb.config import NLP_TASKS


@feats_available
def get_features(reqobj):
    """
    :param containerid:
    :param feats:
    :param words:
    :param path:
    :return:
    """

    print('\n\n\nget_features with feats_available')
    print(reqobj)

    container = reqobj['container']
    resp = celery.send_task(
        NLP_TASKS['retrieve_features'],
        kwargs={
            'containerid': container.pk,
            'feats': reqobj['feats'],
            'path': container.get_folder_path(),
            'words': reqobj['words']
        }
    ).get()
    if resp:
        return {'success': True, 'data': resp}
    else:
        return {
            'success': False,
            'msg': f'no features for feature number {reqobj["feats"]}'
        }
