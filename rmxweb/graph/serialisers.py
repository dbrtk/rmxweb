
from contrib.csv_serialiser import CsvSerialiser
from contrib.json_serialiser import JsonSerialiser
from contrib.serialiser_factory import SerialiserFactory


@SerialiserFactory.set_serialiser('graph_csv')
class GraphCSVSerialiser(CsvSerialiser):

    EDGE_COLUMNS = ['dataid', 'featureid', 'weight']
    FEAT_COLUMNS = ['featureid', 'count']
    DATA_COLUMNS = ['dataid', 'pk', 'url', 'title']
    WORD_COLUMNS = ['word', 'weight', 'featureid']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.feature = self.data['features']
        self.word = self.data['words']
        self.data = self.data['docs']
        self.edge = self.data['edges']

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
            columns=self.FEAT_COLUMNS)

    def get_data(self):

        return self.to_csv(
            rows=self.data,
            file_name='data.csv',
            columns=self.DATA_COLUMNS)

    def get_word(self):

        return self.to_csv(
            rows=self.word,
            file_name='word.csv',
            columns=self.WORD_COLUMNS)

    def get_edge(self):

        return self.to_csv(
            rows=self.edge,
            file_name='edge.csv',
            columns=self.EDGE_COLUMNS)

    def get_conf(self):

        out = {
            'columns': {
                'edge': self.EDGE_COLUMNS,
                'feature': self.FEAT_COLUMNS,
                'word': self.WORD_COLUMNS,
                'data': self.DATA_COLUMNS,
            },
            'count': {
                'feature': len(self.feature),
                'data': len(self.data),
                'edge': len(self.edge),
                'word': len(self.word)
            },
            'data_type_mapping': {
                'feature': {
                    'featureid': 'string',
                    'count': 'integer'
                },
                'data': {
                    'dataid': 'string',
                    'pk': 'integer',
                    'url': 'string',
                    'title': 'string'
                },
                'edge': {
                    'featureid': 'string',
                    'dataid': 'string',
                    'weight': 'float'
                },
                'word': {
                    'word': 'string',
                    'weight': 'float',
                    'featureid': 'string'
                }
            }
        }
        return self.to_json(out, 'config.json')


@SerialiserFactory.set_serialiser('graph_json')
class GraphJsonSerialiser(JsonSerialiser):

    def __init__(self):

        super().__init__()

