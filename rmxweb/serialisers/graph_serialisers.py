
from copy import deepcopy

from .csv_serialiser import CsvSerialiser
from .serialiser_factory import SerialiserFactory

EDGE_COLUMNS = ['dataid', 'featureid', 'weight']
FEAT_COLUMNS = ['featureid', 'count']
DATA_COLUMNS = ['dataid', 'pk', 'url', 'title']
WORD_COLUMNS = ['word', 'weight', 'featureid']

CONFIG = {
    'columns': {
        'edges': EDGE_COLUMNS,
        'features': FEAT_COLUMNS,
        'words': WORD_COLUMNS,
        'docs': DATA_COLUMNS,
    },
    'data_type_mapping': {
        'features': {
            'featureid': 'string',
            'count': 'integer'
        },
        'docs': {
            'dataid': 'string',
            'pk': 'integer',
            'url': 'string',
            'title': 'string'
        },
        'edges': {
            'featureid': 'string',
            'dataid': 'string',
            'weight': 'float'
        },
        'words': {
            'word': 'string',
            'weight': 'float',
            'featureid': 'string'
        }
    }
}


@SerialiserFactory.set_serialiser('graph_csv')
class GraphCSVSerialiser(CsvSerialiser):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.feature = self.data['features']
        self.word = self.data['words']
        self.docs = self.data['docs']
        self.edge = self.data['edges']
        del self.data
        self.write_to_zip(
            self.get_feat(),
            self.get_data(),
            self.get_edge(),
            self.get_word(),
            self.get_conf()
        )

    def get_feat(self):

        return self.to_csv(
            rows=self.feature,
            file_name='feature.csv',
            columns=FEAT_COLUMNS)

    def get_data(self):

        return self.to_csv(
            rows=self.docs,
            file_name='data.csv',
            columns=DATA_COLUMNS)

    def get_word(self):

        return self.to_csv(
            rows=self.word,
            file_name='word.csv',
            columns=WORD_COLUMNS)

    def get_edge(self):

        return self.to_csv(
            rows=self.edge,
            file_name='edge.csv',
            columns=EDGE_COLUMNS)

    def get_conf(self):

        out = deepcopy(CONFIG)
        out['count'] = {
            'features': len(self.feature),
            'docs': len(self.docs),
            'edges': len(self.edge),
            'words': len(self.word)
        }
        return self.to_json(out, 'config.json')
