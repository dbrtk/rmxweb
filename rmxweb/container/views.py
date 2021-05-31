
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from .data import request_features
from data.models import Data
from .decorators import graph_request
from .emit import compute_features, crawl_async
from .models import Container
from serialisers import SerialiserFactory
from .serializers import ContainerSerializer
from rmxweb.celery import celery
from rmxweb import config


class ContainerList(APIView):

    def get(self, request, format=None):
        """Retrieves a list of all existing containers."""
        containers = Container.objects.all().order_by('-created')
        data_seed = Data.filter_seed_data([_.pk for _ in containers])

        serialiser = SerialiserFactory().get_serialiser('container_csv')
        serialiser = serialiser(
            data={'container': containers, 'dataset': data_seed}
        )
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % 'out.zip'
        return resp

    def post(self, request, format=None):
        """
        Creating and saving the record to the database. This method calls the
        task that launches the crawler.

        :param request:
        :param format:
        :return:
        """
        the_name = request.data.get('name')
        endpoint = request.data.get('endpoint')
        url_list = [endpoint]
        crawl = request.data.get("crawl", True)
        if not isinstance(crawl, bool):
            raise ValueError(request.data)

        container = Container.create(the_name=the_name)
        depth = config.DEFAULT_CRAWL_DEPTH if crawl else 0

        crawlid = crawl_async(
            url_list=url_list, containerid=container.pk, depth=depth)
        return JsonResponse({
            'params': {
                'name': the_name,
                'url_list': url_list,
                'endpoint': endpoint,
                'crawl': crawl,
            },
            'crawlid': crawlid,
        })


class ContainerRecord(APIView):

    def get_object(self, pk):
        try:
            return Container.get_object(pk=pk)
        except Container.DoesNotExist:
            raise Http404

    def get(self, request, pk, **_):
        """
        Retrieve a Container object for a given id (pk).
        :param request:
        :param pk:
        :param format:
        :return:
        """
        params = request.GET.dict()
        links = params.get('links', False)
        if not isinstance(links, bool):
            raise Http404(params)
        container = self.get_object(pk)
        if not container.crawl_ready or not container.container_ready:
            container_serializer = ContainerSerializer(self.get_object(pk))
            return JsonResponse({
                'success': False,
                'container': container_serializer.data
            })
        dataset = container.data_set.all()

        # links = []
        # for datum in dataset:
        #     links += datum.get_all_links()
        serialiser = SerialiserFactory().get_serialiser('container_csv')
        serialiser = serialiser(
            data={'container': [container], 'dataset': dataset}
        )
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % 'out.zip'
        return resp

    @staticmethod
    def check_container(containerid: int):
        """
        Checks if a container is ready.
        :param containerid:
        :return:
        """
        pass

    def put(self, request, pk, format=None):
        """
        Updating the container with a new seed endpoint, this will launch the
        crawler on an existing container.
        :param request:
        :param pk:
        :param format:
        :return:
        """
        the_name = request.data.get('name')
        endpoint = request.data.get('endpoint')
        crawl = request.data.get("crawl", True)
        if not isinstance(crawl, bool):
            raise ValueError(request.data)
        container = Container.get_object(pk=pk)
        container.set_crawl_ready(value=False)
        resp = {}

        if the_name:
            container.name = the_name
            container.save()
            resp = {
                'data': request.data,
                'name': the_name,
            }
        if endpoint:
            depth = config.DEFAULT_CRAWL_DEPTH if crawl else 0
            crawlid = crawl_async(
                url_list=[endpoint], containerid=container.pk, depth=depth)
            resp = {
                'endpoint': endpoint,
                'crawlid': crawlid,
                'data': request.data
            }
        return Response(resp, status=200)

    def delete(self, request, pk, format=None):
        """
        Delete a container from the database.
        :param request:
        :param pk:
        :param format:
        :return:
        """
        Container.get_object(pk=pk).delete()
        return JsonResponse({'msg': 'deleted container with id: {pk}'})


class Features(APIView):
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
        response = request_features(
            containerid=containerid,
            features=features,
            words=words,
            featsperdoc=featsperdoc,
            docsperfeat=docsperfeat
        )
        return JsonResponse({
            'data': response.get('features'),
            'params': {
                'containerid': containerid,
                'words': words,
                'featsperdoc': featsperdoc,
                'docsperfeat': docsperfeat,
                'feats': features
            },
        })

    def post(self, request, containerid: int = None, feats: int = 10,
             format=None):
        """Creating features for a container and a feats number."""
        resp = request_features(containerid=containerid, features=feats)
        container = Container.get_object(pk=containerid)
        if not container:
            return Http404(f"The container with id: {containerid} doesn't exist.")
        compute_features()

    def delete(self, request, containerid: int = None, feats: int = 10, format=None):
        """Delete features for a given container."""
        pass


class Documents(APIView):
    """ retrieve documents (web pages) with features.
    """
    @graph_request
    def get(self, containerid: int = None, words: int = 10, features: int = 10,
            docsperfeat: int = 5, featsperdoc: int = 3, **_):
        """
        :param containerid:
        :param words:
        :param features:
        :param docsperfeat:
        :param featsperdoc:
        :return:
        """
        response = request_features(
            containerid=containerid,
            feats=features,
            words=words,
            featsperdoc=featsperdoc,
            docsperfeat=docsperfeat
        )
        return JsonResponse({
            'data': response.get('docs'),
            'params': {
                'containerid': containerid,
                'words': words,
                'featsperdoc': featsperdoc,
                'docsperfeat': docsperfeat,
                'feats': features
            },
        })


def test_celery(request, a, b):

    resp = celery.send_task(
        "scrasync.tasks.test_task",
        args=[a, b],
    ).get(timeout=3)

    return JsonResponse({
        'resp': resp
    })
