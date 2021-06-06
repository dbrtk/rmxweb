from copy import deepcopy

from .csv_serialiser import CsvSerialiser
from .serialiser_factory import SerialiserFactory


BRANCH_COLUMNS = ['id', 'parent']
NODE_COLUMNS = ['id', 'parent', 'size', 'url', 'title', 'pk', 'created']

CONFIG = {
    'columns': {
        'branch': BRANCH_COLUMNS,
        'node': NODE_COLUMNS,
    },
    'data_type_mapping': {
        'branch': {
            'id': 'string',
            'parentid': 'string'
        },
        'node': {
            'id': 'string',
            'parent': 'string',
            'size': 'integer',
            'url': 'string',
            'title': 'string',
            'pk': 'integer',
            'created': 'datetime'
        }
    }
}


@SerialiserFactory.set_serialiser('dendrogram_csv')
class DendrogramCSV(CsvSerialiser):

    def __init__(self, *args, **kwds):

        super(DendrogramCSV, self).__init__(*args, **kwds)

        self.branch = self.data['branch']
        self.leaf = self.data['leaf']
        del self.data

        self.write_to_zip(
            self.get_branch(),
            self.get_leaf(),
            self.get_config()
        )

    def get_branch(self):

        return self.to_csv(
            rows=self.branch,
            file_name='branch.csv',
            columns=BRANCH_COLUMNS)

    def get_leaf(self):

        return self.to_csv(
            rows=self.leaf,
            file_name='leaf.csv',
            columns=NODE_COLUMNS)

    def get_config(self):

        out = deepcopy(CONFIG)
        out['count'] = {
            'branch': len(self.branch),
            'leaf': len(self.leaf)
        }
        return self.to_json(out, 'config.json')
