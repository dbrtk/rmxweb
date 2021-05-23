
import json
import time
import uuid

from django.http import Http404, JsonResponse
from rest_framework.views import APIView

from .data import graph, graph_to_csv, GraphCSV
from container.decorators import feats_available, graph_request
from container.models import Container, FeaturesStatus
from .emit import get_features, hierarchical_tree, search_texts


class Graph(APIView):
    """Returns a specific feature defined by the features number."""

    @graph_request
    def get(self, containerid: int = None, words: int = 10, features: int = 10,
            docsperfeat: int = 5, featsperdoc: int = 3, **_):
        """
        Returns features for a given containerid and parameters defined in the
        request's GET dictionary. The expected parameters are:
        containerid: int = None,
        words: int = 10,
        features: int = 10,
        docsperfeat: int = 5,
        featsperdoc: int = 3

        :param containerid:
        :param words:
        :param features:
        :param docsperfeat:
        :param featsperdoc:
        :return:
        """
        out = {
            'params': {
                'containerid': containerid,
                'words': words,
                'features': features,
                'docsperfeat': docsperfeat,
                'featsperdoc': featsperdoc,
            },
        }
        if FeaturesStatus.computing_feats_busy(containerid, features):
            out.update({
                'retry': True,
                'busy': True,
                'success': False,
            })
        else:
            out['success'] = True
            out['data'] = GraphCSV(
                containerid=containerid, words=words, features=features,
                featsperdoc=featsperdoc, docsperfeat=docsperfeat)
            # out['data'] = graph_to_csv(
            #     containerid=containerid, words=words, features=features,
            #     featsperdoc=featsperdoc, docsperfeat=docsperfeat)
        return JsonResponse(out)


class Dendrogram(APIView):
    """ Returns the dataset for the hierarchical tree / dendrogram.
    """
    def get(self, request):
        """
        Returns the hierarchical tree that can be used to display a dendrogram
        or radial, circular dendrogram.
        :param request:
        :return:
        """
        params = request.GET.dict()
        flat = params.get('flat')
        if flat:
            flat = json.loads(flat)
        else:
            flat = True
        try:
            containerid = int(params.get('containerid'))
        except (ValueError, TypeError):
            raise Http404(params)
        if not isinstance(flat, bool):
            raise Http404(params)
        out = {
            'containerid': containerid,
            'success': False,
        }
        if FeaturesStatus.computing_dendrogram_busy(containerid):
            out['msg'] = 'The dendrogram is currently being computed.'
            out['busy'] = True
        else:
            resp = hierarchical_tree(containerid=containerid, flat=flat)
            data = resp.get('data')
            if data:
                if resp.get('flat'):
                    data = self.process_flat_data(containerid, data)
                out['data'] = data
                out['length'] = len(data)
                out['success'] = True
            else:
                out['response'] = resp
        return JsonResponse(out)

    def process_flat_data(self, containerid, data):
        """
        :param containerid:
        :param data:
        :return:
        """
        try:
            container = Container.get_object(pk=containerid)
        except ValueError:
            raise Http404(containerid)
        dataset = list(container.data_set.all())
        for item in data:
            if item['type'] == 'branch':
                continue
            try:
                rec = next(
                    _ for _ in dataset if _.dataid == item['fileid']
                )
            except StopIteration:
                continue
            else:
                item['url'] = rec.url
                item['title'] = rec.title
                item['pk'] = rec.pk
        data.reverse()
        return data


def list_features(request):
    """ This lists n features for a given containerid and a features number
    (n). It is a helper to get all the features and lemma computed on a
    container.
    :param request:
    :return:
    """
    params = request.GET.dict()
    feats = 10
    try:
        containerid = int(params['containerid'])
        container = Container.get_object(pk=containerid)
        if 'features' in params:
            feats = int(params['features'])
    except (ValueError, KeyError, TypeError) as _:
        raise Http404(params)

    start = time.time()
    out = get_features(containerid=containerid, feats=feats,
                       path=container.get_folder_path())
    lemma = [','.join(_['word'] for _ in item) for item in out]
    end = time.time()
    return JsonResponse({
        'features': out,
        'lemma_str': lemma,
        'time': end - start,
    })


def get_context(request):
    """ Returns the context for lemmatised feature words.

    The parameters object;
    {
        containerid: int,
        lemma: list[str],
        highlight: bool,
    }
    :param request:
    :return:
    """
    params = request.GET.dict()
    try:
        containerid = int(params['containerid'])
        container = Container.get_object(pk=containerid)
        lemma = params['lemma']
    except (ValueError, KeyError, TypeError) as _:
        raise Http404(params)

    highlight = params.get('highlight', False)

    lemma_to_words, lemma = container.get_lemma_words(lemma)
    matchwords = []
    for i in lemma:
        try:
            mapping = next(_ for _ in lemma_to_words if _.get('lemma') == i)
            matchwords.extend(mapping.get('words'))
        except StopIteration:
            matchwords.append(i)
    data = search_texts(
        path=container.container_path(),
        highlight=highlight,
        words=matchwords
    )
    data_objs = {
        _.dataid: {'title': _.title, 'url': _.url}
        for _ in container.data_set.filter(
            file_id__in=list(uuid.UUID(_) for _ in data['data'].keys())
        )
    }
    return JsonResponse({
        'success': True,
        'data': data.get('data'),
        'documents': data_objs,
        'lemma': lemma,
        'words': matchwords,
    })
