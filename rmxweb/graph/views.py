
import json
import uuid

from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.views import APIView

from container.decorators import feats_available, graph_request
from container.models import Container, FeaturesStatus
from .data import get_graph
from .emit import get_features, hierarchical_tree, search_texts
from rmxweb import config
from serialisers import SerialiserFactory


class Graph(APIView):
    """Returns a specific feature defined by the features number."""

    @graph_request
    def get(self, containerid: int = None, words: int = 10, features: int = 10,
            docsperfeat: int = 0, featsperdoc: int = 3, **_):
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
        :param data_format:
        :return:
        """
        out = {
            'params': {
                'containerid': containerid,
                'words': words,
                'features': features,
                'docsperfeat': docsperfeat,
                'featsperdoc': featsperdoc
            },
        }

        if FeaturesStatus.computing_feats_busy(containerid, features):
            out.update({
                'retry': True,
                'busy': True,
                'success': False,
            })
            return JsonResponse(out)
        serialiser_type = 'graph_json' if config.OUTPUT_TYPE_JSON \
            else 'graph_csv'
        try:
            serialiser = SerialiserFactory().get_serialiser(serialiser_type)
        except ValueError:
            raise Http404(out)

        out['success'] = True
        data = get_graph(
            containerid=containerid, words=words, features=features,
            featsperdoc=featsperdoc, docsperfeat=docsperfeat
        )
        serialiser = serialiser(data)

        if config.OUTPUT_TYPE_JSON:
            return JsonResponse(serialiser.get_value())
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % 'out.zip'
        return resp


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
            'params': params
        }
        serialiser_type = 'dendrogram_json' if config.OUTPUT_TYPE_JSON \
            else 'dendrogram_csv'
        try:
            serialiser = SerialiserFactory().get_serialiser(serialiser_type)
        except ValueError:
            raise Http404(out)
        if FeaturesStatus.computing_dendrogram_busy(containerid):
            out['msg'] = 'The dendrogram is currently being computed.'
            out['busy'] = True
            return JsonResponse(out)

        resp = hierarchical_tree(containerid=containerid, flat=flat)

        if not resp['success']:
            # In this case, the system is busy or there is an issue.
            out['response'] = resp
            return JsonResponse(out)
        branch = resp['branch']
        leaf = resp['leaf']
        leaf = self.prepare_data(containerid, leaf)
        if config.OUTPUT_TYPE_JSON:
            out['leaf'] = leaf
            out['branch'] = branch
            out['leaf_length'] = len(leaf)
            out['branch_length'] = len(branch)
            out['success'] = True
            return JsonResponse(out)

        serialiser = serialiser(data={'branch': branch, 'leaf': leaf})
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % 'out.zip'
        return resp

    def prepare_data(self, containerid, data):
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
            try:
                rec = next(
                    _ for _ in dataset if _.dataid == item['fileid']
                )
            except StopIteration:
                continue
            else:
                del item['fileid']
                item['url'] = rec.url
                item['title'] = rec.title
                item['pk'] = rec.pk
                item['created'] = rec.created
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
    try:
        containerid = int(params['containerid'])
        container = Container.get_object(pk=containerid)
        feats = int(params.get('features', 10))
        words = int(params.get('words', 10))
    except (ValueError, KeyError, TypeError) as _:
        raise Http404(params)

    out = get_features(containerid=containerid, feats=feats, words=words,
                       path=container.get_folder_path())
    if not out:
        raise Http404(params)
    lemma = [','.join(_['word'] for _ in item) for item in out]
    return JsonResponse({
        'containerid': containerid,
        'feature_count': feats,
        'word_count': words,
        'features': out,
        'lemma_str': lemma,
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
    params = request.GET.dict() or json.loads(request.body)

    if not params:
        raise Http404
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

    serialiser = SerialiserFactory().get_serialiser('search_text_csv')

    data_objs = [
        {
            'title': _.title, 'url': _.url, 'pk': _.pk, 'dataid': _.dataid,
            'created': _.created
        }
        for _ in container.data_set.filter(
            file_id__in=list(uuid.UUID(_['dataid']) for _ in data['data'])
        )
    ]
    serialiser = serialiser(data={
        'docs': data_objs, 'response': data, 'lemma': lemma
    })
    if config.OUTPUT_TYPE_JSON:
        return JsonResponse({
            'success': True,
            'data': data.get('data'),
            'documents': data_objs,
            'lemma': lemma,
            'words': matchwords,
        })

    resp = HttpResponse(
        serialiser.get_value(),
        content_type='application/force-download'
    )
    resp['Content-Disposition'] = 'attachment; filename="%s"' % 'out.zip'
    return resp
