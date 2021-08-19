"""

"""
from copy import deepcopy

from .csv_serialiser import CsvSerialiser
from .serialiser_factory import SerialiserFactory

CONTAINER_COLUMNS = [
    'pk', 'name', 'crawl_ready', 'integrity_check_in_progress',
    'container_ready', 'created', 'updated', 'uid'
]

DOC_COLUMNS = [
    'pk', 'containerid', 'created', 'updated', 'url', 'hostname', 'seed',
    'title', 'file_id', 'hash_text'
]

CONFIG = {
    'columns': {
        'container': CONTAINER_COLUMNS,
        'data': DOC_COLUMNS
    },
    'data_type_mapping': {
        'container': {
            'pk': 'integer',
            'name': 'string',
            'crawl_ready': 'boolean',
            'integrity_check_in_progress': 'boolean',
            'container_ready': 'boolean',
            'created': 'datetime',
            'updated': 'datetime',
            'uid': 'string'
        },
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
        }
    }
}


@SerialiserFactory.set_serialiser('container_csv')
class ContainerCsv(CsvSerialiser):

    def __init__(self, *args, process_links: bool = False, **kwargs):

        super().__init__(*args, **kwargs)

        self.container = []
        self.docs = []
        self.links = []

        self.iter_container()
        self.iter_docs()

        params = [self.get_container(), self.get_docs(), self.get_conf()]
        if process_links:
            self.iter_links()
            params.append(self.get_links())
        self.write_to_zip(*params)

    def iter_container(self):
        for item in self.data['container']:
            self.container.append(self.serialise_container(item))

    def iter_docs(self):
        self.data['dataset'].reverse()
        while self.data['dataset']:
            doc = self.data['dataset'].pop(-1)
            self.docs.append(self.serialise_doc(doc))

    def iter_links(self):
        self.data['links'].reverse()
        while self.data['links']:
            link = self.data['links'].pop(-1)
            self.links.append(self.serialise_link(link))

    @staticmethod
    def serialise_container(c):

        return {
            'pk': c.pk,
            'name': c.name,
            'crawl_ready': c.crawl_ready,
            'integrity_check_in_progress': c.integrity_check_in_progress,
            'container_ready': c.container_ready,
            'created': c.created.isoformat(),
            'updated': c.updated.isoformat(),
            'uid': c.uid
        }

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

    def serialise_link(self, doc):

        raise NotImplementedError

    def get_links(self):

        raise NotImplementedError

    def get_container(self):

        return self.to_csv(
            rows=self.container,
            file_name='container.csv',
            columns=CONTAINER_COLUMNS)

    def get_docs(self):

        return self.to_csv(
            rows=self.docs,
            file_name='data.csv',
            columns=DOC_COLUMNS)

    def get_conf(self):

        out = deepcopy(CONFIG)
        out['count'] = {
            'container': len(self.container),
            'data': len(self.docs)
        }
        return self.to_json(out, 'config.json')
