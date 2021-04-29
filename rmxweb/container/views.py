
from django.http import Http404, JsonResponse
from rest_framework.views import APIView

from .models import Container
from .serializers import ContainerSerializer
from rmxweb.celery import celery
from rmxweb import config


class ContainerList(APIView):

    def get(self, request, format=None):

        containers = Container.objects.all().order_by('-created')
        serializer = ContainerSerializer(containers, many=True)
        return JsonResponse(serializer.data)

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
        crawl = True if crawl else crawl

        container, resp = Container.create(the_name=the_name)
        print(f'\n\n\nthe container: {container}\nthe response: {resp}')
        print(f'\n\n\ncontainer type: {type(container)}\nresponse type: {type(resp)}')
        depth = config.DEFAULT_CRAWL_DEPTH if crawl else 0

        print(f'\n\n\n\n\n post called on the container - creating a container record! ')

        # todo(): pass the corpus file path to the crawler.
        # celery.send_task(
        #     config.RMXBOT_TASKS['crawl_async'],
        #     kwargs={
        #         'url_list': url_list,
        #         'corpus_id': docid,
        #         'depth': depth
        #     }
        # )

        return JsonResponse({
            'params': {
                'name': the_name,
                'url_list': url_list,
                'endpoint': endpoint,
                'crawl': crawl,
            },
            'rpc_queues': config.RPC_PUBLISH_QUEUES,
            'post': request.data
        })


class ContainerRecord(APIView):

    def get_object(self, pk):
        try:
            return Container.objects.get(pk=pk)
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
        serializer = ContainerSerializer(container)
        return JsonResponse(serializer.data)

    def put(self, request, pk, format=None):

        pass

    def delete(self, request, pk, format=None):

        pass


def test_celery(request, a, b):

    print('\n\n\ntest_celery called!')
    print(
        f'task route: {config.RMXWEB_TASKS.get("test_task")};\na: {a}; b: {b}'
    )
    resp = celery.send_task(
        config.RMXWEB_TASKS.get('test_task'),
        args=[a, b],
        queue='rmxweb'
    ).get(timeout=3)

    return JsonResponse({
        'resp': resp
    })


# todo(): delete these views
# class Urls(APIView):
#
#     pass
#
#
# class UrlRecord(APIView):
#
#     pass
#
#
# class CrawlStatus(APIView):
#     pass
#
#
# class CrawlStatusRecord(APIView):
#     pass
