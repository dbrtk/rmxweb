
import json
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.views import APIView

from .models import Data
from .serializers import DatasetSerializer, LinksSerializer
from serialisers import SerialiserFactory


class ListData(APIView):
    """This view class lists all data objects for a given container id."""
    def get(self, request):
        """Retrieves a list of Data objects for a given containerid."""
        params = request.GET.dict()
        try:
            containerid = int(params.get('containerid'))
            get_links = params.get('links')
            if isinstance(get_links, str):
                get_links = json.loads(get_links)
            else:
                get_links = bool(int(get_links))
        except (TypeError, ValueError, json.decoder.JSONDecodeError) as _:
            raise Http404(f'Provided parameters: {params}')
        links = []
        data_objs = Data.objects.filter(container__pk=containerid)
        if get_links:
            for item in data_objs:
                links += item.get_all_links()

        serialiser = SerialiserFactory().get_serialiser('data_list_csv')
        serialiser = serialiser(data={'dataset': data_objs, 'links': links})
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % 'out.zip'
        return resp


class DataRecord(APIView):
    """View exposing a single Data record."""
    def get(self, request, pk):
        """Retrieves a record for a given pk.
        :param request:
        :param pk:
        :return:
        """
        try:
            data_obj = Data.get_object(pk=pk)
        except ValueError as _:
            raise Http404(pk)
        links = data_obj.get_all_links()

        serialiser = SerialiserFactory().get_serialiser('data_csv')
        serialiser = serialiser(
            data={'doc': data_obj, 'links': links, 'text': data_obj.get_text()}
        )
        resp = HttpResponse(
            serialiser.get_value(),
            content_type='application/force-download'
        )
        resp['Content-Disposition'] = 'attachment; filename="%s"' % 'out.zip'
        return resp
