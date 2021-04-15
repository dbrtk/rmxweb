
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view

from . import models
from . import serializers


def home(request):
    return HttpResponse('This is the home of the "container" app.')


class ContainerViewSet(viewsets.ModelViewSet):

    queryset = models.Container.objects.all().order_by('-created')
    serializer_class = serializers.ContainerSerializer


@api_view(['POST'])
def create(request):

    if request.method != 'POST':
        raise RuntimeError(request)

    the_name = request.POST.get('name')
    endpoint = request.POST.get('endpoint')
    url_list = [endpoint]
    crawl = request.POST.get("crawl", True)
    crawl = True if crawl else crawl

    import pdb
    pdb.set_trace()

    return HttpResponse('Container created')


