
from functools import wraps
import json
from json.decoder import JSONDecodeError

from django.http import Http404

from rmxweb import config


def graph_request(func):
    """Decorating view methods that contain a graph request."""

    # todo(): delete this!
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
        params = request.query_params.dict()
        if containerid is not None:
            params['containerid'] = containerid
        required = ['containerid', 'features']
        structure = {
            'containerid': int,
            'words': int,
            'features': int,
            'data-for-feature': int,
            'features-for-datum': int,
            'format': str,
        }
        if not all(_ in params for _ in required):
            raise Http404({
                'error': True,
                'prams': params,
                'expected': list(structure.keys())
            })
        for k, v in params.items():
            try:
                if structure[k] is int:
                    params[k] = int(v)
                elif structure[k] is bool:
                    params[k] = json.loads(v)
            except (ValueError, KeyError, JSONDecodeError):
                raise Http404({
                    'error': True, 'key': k, 'value': v, 'params': params,
                    'accepted': list(structure.keys())
                })
        _format = params.get('format')
        if _format:
            if _format not in config.AVAILABLE_FORMATS:
                raise Http404({
                    'error': True,
                    'key': 'format',
                    'value': _format,
                    'params': params,
                    'accepted': config.AVAILABLE_FORMATS
                })
        else:
            _format = 'csv'
        return func(
            self,
            containerid=params.get('containerid'),
            words=params.get('words', 20),
            features=params.get('features', 10),
            docsperfeat=params.get('data-for-feature', 5),
            featsperdoc=params.get('features-for-datum', 3),
            flat=params.get('flat', True),
            data_format=_format,
            uri=request.get_full_path()
        )
    return wrapper
