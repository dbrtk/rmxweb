
from functools import wraps

from .models import Container
from rmxweb.celery import celery
from rmxweb import config


def feats_httpreq(func):

    @wraps(func)
    def wrapped_view(request):
        pass
    return wrapped_view


def feats_available(func):
    """Decorator that checks if requested features have been computed. If it's
       not the case, they are generated. This decorator is used by the graphql
       api.

       This decorates functions and not django's views.
    """
    @wraps(func)
    def wrapped_view(containerid: int = None, words: int = 10,
                     features: int = 10, docsperfeat: int = 5,
                     featsperdoc: int = 3, **kwds):

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
            out = {
                'words': words,
                'feats': features,
                'docs_per_feat': docsperfeat,
                'feats_per_doc': featsperdoc,
                'container': container,
                'containerid': container.pk
            }
            out.update(kwds)
            return func(**out)
        celery.send_task(
            config.RMXWEB_TASKS['generate_matrix_remote'],
            kwargs={
                'containerid': container.pk,
                'features': features,
                'words': words,
                'docs_per_feat': docsperfeat,
                'feats_per_doc': featsperdoc
            }
        )
        out.update(availability)
        return out
    return wrapped_view
