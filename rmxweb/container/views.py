
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from data.serializers import DatasetSerializer
from .emit import crawl_async
from .models import Container
from .serializers import ContainerSerializer
from rmxweb.celery import celery
from rmxweb import config


class ContainerList(APIView):

    def get(self, request, format=None):

        containers = Container.objects.all().order_by('-created')
        serializer = ContainerSerializer(containers, many=True)
        return JsonResponse({'data': serializer.data})

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
            'rpc_queues': config.RPC_PUBLISH_QUEUES,
            'post': request.data
        })


class ContainerRecord(APIView):

    def get_object(self, pk):
        try:
            return Container.get_object(pk=pk)
        except Container.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """
        Retrieve a Container object for a given id (pk).
        :param request:
        :param pk:
        :param format:
        :return:
        """
        container = self.get_object(pk)
        container_serializer = ContainerSerializer(self.get_object(pk))
        data_serializer = DatasetSerializer(container.data_set.all(), many=True)
        dataset = data_serializer.data
        return JsonResponse({
            'dataset': data_serializer.data,
            'dataset_length': len(dataset),
            'container': container_serializer.data,
            'containerid': pk})

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


def test_celery(request, a, b):

    resp = celery.send_task(
        "scrasync.tasks.test_task",
        args=[a, b],
    ).get(timeout=3)

    return JsonResponse({
        'resp': resp
    })
