
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.views import APIView

from .models import Container
from .serializers import ContainerSerializer

from django.conf import settings


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

        print(f'\n\n\n\n\n post called on the container - creating a container record! ')

        return JsonResponse({
            'params': {
                'name': the_name,
                'url_list': url_list,
                'endpoint': endpoint,
                'crawl': crawl,
            },
            'rpc_queues': settings.RPC_PUBLISH_QUEUES,
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
