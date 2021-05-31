
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.views import APIView

from container.models import Container, FeaturesStatus
from .emit import get_features
from serialisers import SerialiserFactory


class Feature(APIView):
    """
    Displaying features for a container id and feature's number.
    """
    def get(self, request):

        params = request.GET.dict()
        try:
            containerid = int(params['containerid'])
            feats = int(params.get('features', 10))
            words = int(params.get('words', 10))
            docs_for_feat = params.get('documents-for-feature', 0)
        except (ValueError, KeyError, TypeError) as _:
            raise Http404(params)
        container = Container.get_object(pk=containerid)

        stat = self.check_features_status(containerid, feats)
        if not stat['success']:
            return JsonResponse(stat)

        resp = self.get_features(
            containerid, feats, words, container.get_folder_path())
        if not resp['success']:
            return JsonResponse(resp)
        serialiser = SerialiserFactory().get_serialiser('features_csv')
        serialiser = serialiser(data=resp)

        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % 'out.zip'
        return resp

    @staticmethod
    def check_features_status(containerid: int, features: int):
        """
        :param containerid:
        :param features:
        :return:
        """
        if FeaturesStatus.computing_feats_busy(
                containerid=containerid, feats=features):
            return {
                'containerid': containerid,
                'features': features,
                'retry': True,
                'busy': True,
                'success': False,
            }
        return {'success': True}

    @staticmethod
    def get_features(containerid: int, feats: int, words: int, path: str):
        """
        Getting features and lexemes.
        :param containerid:
        :param feats:
        :param words:
        :param path:
        :return:
        """
        out = get_features(containerid=containerid, feats=feats, words=words,
                           path=path)
        if not out['success']:
            return out

        out['data'].sort(key=lambda _: _['id'])
        _lemma = {}
        for item in out['data']:
            if item['id'] not in _lemma:
                _lemma[item['id']] = []
            _lemma[item['id']].append(item['word'])
        out['lemma'] = [
            {'id': k, 'lemma': ','.join(v)} for k, v in _lemma.items()
        ]
        return out
