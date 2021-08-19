
import json
import uuid

from django.http import Http404, HttpResponse
from rest_framework.views import APIView, Response

from container.models import Container, FeaturesStatus
from .data import get_graph
from .decorators import graph_request
from .emit import hierarchical_tree, search_texts
from prom.config import (
    COMPUTE_DENDROGRAM_CALLBACK_PREFIX,
    COMPUTE_DENDROGRAM_RUN_PREFIX,
    COMPUTE_MATRIX_CALLBACK_PREFIX,
    COMPUTE_MATRIX_RUN_PREFIX
)
from prom.query import QueryPrometheus, RunProcessMetrics
from serialisers import SerialiserFactory


class _View(APIView):

    @staticmethod
    def http_resp_for_busy(
            *, containerid: (int, str), payload: dict = None, uri: str = None,
            msg: str = None):
        """
        :param containerid:
        :param payload:
        :param uri:
        :param msg:
        :return:
        """
        return {
            'task': {
                '@uri': uri,
                'id': containerid,
                'name': msg,
                'job-state': "STARTED",
                'job-status': "INPROGRESS",
                'response-payload': payload
            }
        }


class Graph(_View):
    """Returns a network graph for a given container id and features number.
    """

    @graph_request
    def get(self, containerid: int = None, words: int = 10, features: int = 10,
            docsperfeat: int = 0, featsperdoc: int = 3, uri: str = None, **_):
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
        :param uri:
        :return:
        """
        metrics = RunProcessMetrics(
            run_dtype=COMPUTE_MATRIX_RUN_PREFIX,
            callback_dtype=COMPUTE_MATRIX_CALLBACK_PREFIX,
            containerid=containerid,
            features=features
        )
        stats = metrics.stat_for_last_call()

        print(f"\n\n\nGenerating the graph")
        print(f'the stats for graph / matrix computation: {stats}; '
              f'ready: {stats.get("ready")}; not ready: '
              f'{not stats.get("ready")}\n')

        if not stats.get('ready'):
            return Response(
                super().http_resp_for_busy(
                    containerid=containerid,
                    uri=uri,
                    msg='Graph being computed',
                    payload={
                        'containerid': containerid,
                        'words': words,
                        'features': features,
                        'docsperfeat': docsperfeat,
                        'featsperdoc': featsperdoc
                    }
                ), status=202)

        serialiser = SerialiserFactory().get_serialiser('graph_csv')
        data = get_graph(
            containerid=containerid, words=words, features=features,
            featsperdoc=featsperdoc, docsperfeat=docsperfeat
        )
        if not data.get('success', True):
            return Response(
                super().http_resp_for_busy(
                    containerid=containerid,
                    payload=data,
                    uri=uri,
                    msg='Graph being computed',

                ),
                status=202
            )
        serialiser = serialiser(data)
        zip_name = serialiser.get_zip_name(
            f'Network-Graph-ContainerID-{containerid}')
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
        return resp


class Dendrogram(_View):
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
        serialiser = SerialiserFactory().get_serialiser('dendrogram_csv')

        metrics = RunProcessMetrics(
            run_dtype=COMPUTE_DENDROGRAM_RUN_PREFIX,
            callback_dtype=COMPUTE_DENDROGRAM_CALLBACK_PREFIX,
            containerid=containerid,
        )
        stats = metrics.stat_for_last_call()
        print(f"The dendrogram metrics: {stats}\n")

        if not stats.get('ready'):
            return Response(self.http_resp_for_busy(
                containerid=containerid,
                uri=request.get_full_path(),
                msg='Dendrogram being computed',
                payload=stats,
            ), status=202)

        resp = hierarchical_tree(containerid=containerid, flat=flat)
        if not resp['success']:
            # In this case, the system is busy or there is an issue.
            if resp.get('error', False):
                raise Http404(resp)
            return Response(self.http_resp_for_busy(
                containerid=containerid,
                payload=resp,
                msg="Dendrogram being computed",
                uri=request.get_full_path()
            ), status=202)
        branch = resp['branch']
        leaf = resp['leaf']
        leaf = self.prepare_data(containerid, leaf)
        serialiser = serialiser(data={'branch': branch, 'leaf': leaf})
        zip_name = serialiser.get_zip_name(
            f'Dendrogram-ContainerID-{containerid}')
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
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
    zip_name = serialiser.get_zip_name(
        f'Feature-Context-ContainerID-{containerid}')
    resp = HttpResponse(
        serialiser.get_value(),
        content_type='application/force-download'
    )
    resp['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
    return resp
