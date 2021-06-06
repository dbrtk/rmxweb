
from django.http import Http404, HttpResponse
from rest_framework.views import APIView, Response

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
            # docs_for_feat = params.get('documents-for-feature', 0)
        except (ValueError, KeyError, TypeError) as _:
            raise Http404(params)

        stat = self.check_features_status(containerid, feats)
        if not stat['success']:
            return Response(self.http_resp_for_busy(
                id=containerid,
                uri=request.get_full_path(),
                payload=stat
            ), status=202)

        resp = self.get_features(containerid, feats, words)
        if not resp['success']:
            return Response(self.http_resp_for_busy(
                id=containerid,
                uri=request.get_full_path(),
                payload=resp
            ), status=202)
        serialiser = SerialiserFactory().get_serialiser('features_csv')
        serialiser = serialiser(data=resp)
        zip_name = serialiser.get_zip_name(
            f'Features-ContainerID-{containerid}')
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
        return resp

    def http_resp_for_busy(self, id: (int, str), payload: dict, uri: str):
        """
        :param payload:
        :param uri:
        :return:
        """
        return {
            'task': {
                '@uri': uri,
                'id': id,
                'name': 'Features not ready.',
                'job-state': "STARTED",
                'job-status': "INPROGRESS",
                'summary': payload
            }
        }

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
    def get_features(containerid: int, feats: int, words: int):
        """
        Getting features and lexemes.
        :param containerid:
        :param feats:
        :param words:
        :param path:
        :return:
        """
        out = get_features(containerid=containerid, features=feats, words=words)
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
