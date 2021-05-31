from copy import deepcopy

from .csv_serialiser import CsvSerialiser
from .serialiser_factory import SerialiserFactory

FEATURE_COLUMNS = ['id', 'word', 'weight']
LEMMA_COLUMNS = ['id', 'lemma']

CONFIG = {
    'columns': {
        'features': FEATURE_COLUMNS,
        'lemma': LEMMA_COLUMNS
    },
    'data_type_mapping': {
        'features': {
            'id': 'string',
            'word': 'string',
            'weight': 'float'
        },
        'lexeme': {
            'id': 'string',
            'lemma': 'string'
        },
    }
}


@SerialiserFactory.set_serialiser('features_csv')
class FeatureSerialiser(CsvSerialiser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.features = self.data['data']
        self.lemma = self.data['lemma']

        self.write_to_zip(
            self.get_features(),
            self.get_lemma(),
            self.get_conf()
        )

    def get_features(self):

        return self.to_csv(
            rows=self.features,
            file_name='feature.csv',
            columns=FEATURE_COLUMNS)

    def get_lemma(self):

        return self.to_csv(
            rows=self.lemma,
            file_name='lemma.csv',
            columns=LEMMA_COLUMNS)

    def get_conf(self):
        out = deepcopy(CONFIG)
        out['count'] = {
            'features': len(self.features),
            'lemma': len(self.lemma)
        }
        return self.to_json(out, 'config.json')
