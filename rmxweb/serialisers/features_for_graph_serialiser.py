"""A serialiser for search text and context."""
from copy import deepcopy

from .csv_serialiser import CsvSerialiser
from .serialiser_factory import SerialiserFactory


CONFIG = {
    'columns': {
    },
    'data_type_mapping': {
    }
}


# @SerialiserFactory.set_serialiser('list_features_csv')
class ListFeaturesCsv(CsvSerialiser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
