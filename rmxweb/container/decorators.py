
from functools import wraps

from .models import Container
from rmxweb.celery import celery
from rmxweb import config


def feats_available(func):
    """Decorator that checks if requested features have been computed. If it's
       not the case, they are generated. This decorator is used by the graphql
       api.
    """
    @wraps(func)
    def wrapped_view(containerid: int = None, words: int = 10,
                     features: int = 10, docsperfeat: int = 5,
                     featsperdoc: int = 3):

        container = Container.get_object(pk=containerid)
        availability = container.features_availability(feature_number=features)
        out = {
            'busy': True,
            'retry': True,
            'success': False,
            'available': False,
            'features': features,
            'containerid': container.pk
        }
        if availability.get('busy'):
            return out

        if availability.get('available'):
            return func({
                'words': words,
                'feats': features,
                'docs_per_feat': docsperfeat,
                'feats_per_doc': featsperdoc,
                'container': container
            })

        celery.send_task(
            config.RMXWEB_TASKS['generate_matrices_remote'],
            kwargs={
                'containerid': container.pk,
                'feats': features,
                'vectors_path': container.get_vectors_path(),
                'words': words,
                'docs_per_feat': docsperfeat,
                'feats_per_doc': featsperdoc
            }
        )
        out.update(availability)
        return out
    return wrapped_view
