
from django.http import Http404, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from container.data import graph
from container.decorators import graph_request


class Graph(APIView):
    """Returns a specific feature defined by the features number."""

    @graph_request
    def get(self, containerid: int = None, words: int = 10, features: int = 10,
            docsperfeat: int = 5, featsperdoc: int = 3):
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
        out = graph(containerid=containerid, words=words, features=features,
                    featsperdoc=featsperdoc, docsperfeat=docsperfeat)
        return JsonResponse({
            'msg': 'response from graph getter',
            'params': {
                'containerid': containerid,
                'words': words,
                'features': features,
                'docsperfeat': docsperfeat,
                'featsperdoc': featsperdoc,
            },
            'graph': out,
        })


class Hierarchical(APIView):
    """

    """
    @graph_request
    def get(self, containerid: int = None, words: int = 10, features: int = 10,
            docsperfeat: int = 5, featsperdoc: int = 3):

        pass
