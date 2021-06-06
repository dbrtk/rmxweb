"""
Serialising Data objects.
"""
from copy import deepcopy
import multiprocessing as mp

from .csv_serialiser import CsvSerialiser
from .data_list_serialiser import CONFIG
from .serialiser_factory import SerialiserFactory

LINK_COLUMNS = ['pk', 'created', 'url', 'hostname', 'dataid']
DOC_COLUMNS = [
    'pk', 'containerid', 'created', 'updated', 'url', 'hostname', 'seed',
    'title', 'file_id', 'hash_text'
]


@SerialiserFactory.set_serialiser('data_csv')
class DataCsv(CsvSerialiser):

    cpu_count = mp.cpu_count()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.docs = [self.serialise_doc(self.data['doc'])]
        self.links = []
        self.text = []

        self.iter_links()
        self.write_to_zip(
            self.get_links(),
            self.get_docs(),
            self.get_text()
        )

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

    def get_text(self):

        return self.to_txt(
            lines=[f'{_}\n' for _ in self.data['text']],
            file_name='text.txt',
        )

    def get_conf(self):

        out = deepcopy(CONFIG)
        out['count'] = {
            'links': len(self.links),
            'data': len(self.docs)
        }
        return self.to_json(out, 'config.json')
