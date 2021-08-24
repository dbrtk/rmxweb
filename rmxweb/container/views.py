from django.http import Http404, HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from data.models import Data
from .emit import crawl_async
from .models import Container
from serialisers import SerialiserFactory
from .serializers import ContainerSerializer
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
        zip_name = serialiser.get_zip_name('Containers-List')
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
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
            return Response(request.data, status=404)

        container = Container.create(the_name=the_name)
        depth = config.DEFAULT_CRAWL_DEPTH if crawl else 0
        crawlid = crawl_async(
            url_list=url_list, container=container, depth=depth)
        return Response({
            'task': {
                'href': request.get_full_path(),
                'job-state': "STARTED",
                'job-status': "INPROGRESS",
                'id': container.pk,
                'parameters': {
                    'crawlid': crawlid
                }
            }
        }, status=202)


class ContainerRecord(APIView):

    @staticmethod
    def get_object(pk):
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

        if not container.dataset_is_ready(client_request=True):
            container_serializer = ContainerSerializer(self.get_object(pk))
            return Response({
                'task': {
                    '@uri': request.get_full_path(),
                    'id': container.pk,
                    'name': 'Container not ready.',
                    'job-state': "STARTED",
                    'job-status': "INPROGRESS",
                    'summary': container_serializer.data
                }
            }, status=202)
        dataset = container.data_set.all()

        # links = []
        # for datum in dataset:
        #     links += datum.get_all_links()
        serialiser = SerialiserFactory().get_serialiser('container_csv')
        serialiser = serialiser(
            data={'container': [container], 'dataset': dataset}
        )
        zip_name = serialiser.get_zip_name(f'Container-ID-{container.pk}')
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
        return resp

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
            raise Http404(request.data)
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
                url_list=[endpoint], container=container, depth=depth)
            resp = {
                'task': {
                    'href': request.get_full_path(),
                    'id': container.pk,
                    'parameters': {
                        'crawlid': crawlid,
                    }
                }
            }
        return Response(resp, status=202)

    def delete(self, request, pk, format=None):
        """
        Delete a container from the database.
        :param request:
        :param pk:
        :param format:
        :return:
        """
        obj = self.get_object(pk)
        obj.delete_container()
        return Response({
            'task': {
                '@uri': request.get_full_path(),
                'id': pk,
                'name': 'Container deleted.',
            }
        }, status=202)
