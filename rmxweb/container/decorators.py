
from functools import wraps

from django.http import Http404, JsonResponse

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


def graph_request(func):
    """Decorating view methods that contain a graph request."""

    @wraps(func)
    def wrapper(self, request, containerid: int = None, **kwargs):
        """

        request parameters:
        containerid: int = None
        words: int = 10
        features: int = 10
        dataforfeature: int = 5
        featuresfordatum: int = 3

        :param self:
        :param request:
        :param containerid:
        :return:
        """
        params = request.GET.dict()
        if containerid is not None:
            params['containerid'] = containerid
        required = ['containerid', 'features']
        structure = {
            'containerid': int,
            'words': int,
            'features': int,
            'data-for-feature': int,
            'features-for-datum': int,
            'graph-type': str,
        }

        if not all(_ in params for _ in required):
            return JsonResponse({
                'error': True, 'prams': params,
                'expected': list(structure.keys())
            })
        for k, v in params.items():
            try:
                params[k] = int(v)
                _ = structure[k]
            except (ValueError, KeyError):
                return JsonResponse({
                    'error': True, 'key': k, 'value': v, 'params': params,
                    'expected': list(structure.keys())
                })
        return func(
            self,
            containerid=params.get('containerid'),
            words=params.get('words', 20),
            features=params.get('features', 10),
            docsperfeat=params.get('data-for-feature', 5),
            featsperdoc=params.get('features-for-datum', 3)
        )
    return wrapper
