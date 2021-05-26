

from functools import wraps
import json
from json.decoder import JSONDecodeError

from django.http import JsonResponse

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
        print(f'\n\navailable feats; container: {container}')
        availability = container.features_availability(feature_number=features)
        print(f'availability: {availability}')
        out = {
            'busy': True,
            'retry': True,
            'success': False,
            'available': False,
            'features': features,
            'containerid': container.pk
        }
        if availability.get('busy'):
            print(f'return is busy: {out}')
            return out
        print(f"is not busy; is available: {availability.get('available')}")
        if availability.get('available'):
            out = {
                'words': words,
                'feats': features,
                'docs_per_feat': docsperfeat,
                'feats_per_doc': featsperdoc,
                'container': container,
            }
            out.update(kwds)
            print(f'is available, out: {out}')
            print(f'the function being returned: {func}')
            return func(out)
        print(f'CALLING RMXWEB_TASKS[\'generate_matrices_remote\']')
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
            'type': str,
        }

        if not all(_ in params for _ in required):
            return JsonResponse({
                'error': True, 'prams': params,
                'expected': list(structure.keys())
            })
        for k, v in params.items():
            try:
                if structure[k] is int:
                    params[k] = int(v)
                elif structure[k] is bool:
                    params[k] = json.loads(v)
            except (ValueError, KeyError, JSONDecodeError):
                return JsonResponse({
                    'error': True, 'key': k, 'value': v, 'params': params,
                    'accepted': list(structure.keys())
                })
        return func(
            self,
            containerid=params.get('containerid'),
            words=params.get('words', 20),
            features=params.get('features', 10),
            docsperfeat=params.get('data-for-feature', 5),
            featsperdoc=params.get('features-for-datum', 3),
            flat=params.get('flat', True),
        )
    return wrapper
