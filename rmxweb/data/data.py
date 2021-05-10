

from .models import Data
from .serializers import DatasetSerializer


def webpage(pk: int = None):
    """
    Displays the page - the doc and its structure. This object holds all the
    links that have been found on the scraped page.

    :param pk:
    :return:
    """
    try:
        document = Data.get_object(pk=pk)
    except ValueError as _:
        return {'success': False, 'msg': 'No doc found.'}

    serializer = DatasetSerializer(document)
    return serializer.data
