
from django.http import Http404, JsonResponse
from rest_framework.views import APIView

from .models import Data
from .serializers import DatasetSerializer, LinksSerializer


class ListData(APIView):
    """View that lists all data objects for a given container id."""
    def get(self, request):
        """Retrieves a list of Data objects for a given containerid."""
        params = request.GET.dict()
        containerid = int(params.get('containerid'))
        if not containerid:
            raise Http404(f'A containerid is required. Params: {params}')
        data_objs = Data.objects.filter(container__pk=containerid)
        data_serializer = DatasetSerializer(data_objs, many=True)
        dataset = data_serializer.data
        return JsonResponse({
            'dataset': dataset,
            'dataset_length': len(dataset),
            'containerid': containerid
        })


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
        data_serializer = DatasetSerializer(data_obj)
        links = LinksSerializer(data_obj.get_all_links(), many=True)
        return JsonResponse({
            'text': data_obj.get_text(),
            'links': links.data,
            'data': data_serializer.data,
        })
