"""Serialiser for lists of data objects."""
from copy import deepcopy
import multiprocessing as mp

from .serialiser_factory import SerialiserFactory
from .csv_serialiser import CsvSerialiser


LINK_COLUMNS = ['pk', 'created', 'url', 'hostname', 'dataid']
DOC_COLUMNS = [
    'pk', 'containerid', 'created', 'updated', 'url', 'hostname', 'seed',
    'title', 'file_id', 'hash_text'
]
CONFIG = {
    'columns': {
        'data': DOC_COLUMNS,
        'link': LINK_COLUMNS,
    },
    'data_type_mapping': {
        'data': {
            'pk': 'integer',
            'containerid': 'integer',
            'created': 'datetime',
            'updated': 'datetime',
            'url': 'string',
            'hostname': 'string',
            'seed': 'boolean',
            'title': 'string',
            'file_id': 'string',
            'hash_text': 'string'
        },
        'link': {
            'pk': 'integer',
            'created': 'datetime',
            'url': 'string',
            'hostname': 'string',
            'dataid': 'string'
        }
    }
}


@SerialiserFactory.set_serialiser('data_list_csv')
class DataListCsv(CsvSerialiser):

    cpu_count = mp.cpu_count()

    def __init__(self, *args, **kwargs):

        super(DataListCsv, self).__init__(*args, **kwargs)
        self.docs = []
        self.links = []
        self.iter_docs()
        self.iter_links()
        self.write_to_zip(
            self.get_links(),
            self.get_docs(),
            self.get_conf()
        )

    def iter_docs(self):

        _items = list(self.data['dataset'])
        del self.data['dataset']
        while _items:
            doc = _items.pop(0)
            self.docs.append(self.serialise_doc(doc))

    def iter_links(self):

        _items = list(self.data['links'])
        del self.data['links']
        with mp.Pool(processes=self.cpu_count - 1) as pool:
            self.links = pool.map(self.serialise_link, _items)

    @staticmethod
    def serialise_doc(doc):

        return {
            'pk': doc.pk,
            'containerid': doc.container.id,
            'created': doc.created.isoformat(),
            'updated': doc.updated.isoformat(),
            'url': doc.url,
            'hostname': doc.hostname,
            'seed': doc.seed,
            'title': doc.title,
            'file_id': doc.file_id,
            'hash_text': doc.hash_text
        }

    @staticmethod
    def serialise_link(link):

        return {
            'pk': link.pk,
            'created': link.created.isoformat(),
            'url': link.url,
            'dataid': link.data.id,
            'hostname': link.hostname
        }

    def get_links(self):
        return self.to_csv(
            rows=self.links,
            file_name='link.csv',
            columns=LINK_COLUMNS)

    def get_docs(self):
        return self.to_csv(
            rows=self.docs,
            file_name='data.csv',
            columns=DOC_COLUMNS)

    def get_conf(self):

        out = deepcopy(CONFIG)
        out['count'] = {
            'links': len(self.links),
            'data': len(self.docs)
        }
        return self.to_json(out, 'config.json')
