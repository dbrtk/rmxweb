"""
Serialising Data objects.
"""
from .serialiser_factory import SerialiserFactory
from .csv_serialiser import CsvSerialiser
from rmxweb.config import DATETIME_STRING_FORMAT

LINK_COLUMNS = ['pk', 'created', 'url', 'hostname', 'dataid']
DOC_COLUMNS = [
    'pk', 'containerid', 'created', 'updated', 'url', 'hostname', 'seed',
    'title', 'file_id', 'hash_text'
]


@SerialiserFactory.set_serialiser('data_csv')
class DataCsv(CsvSerialiser):

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
        while _items:
            link = _items.pop(0)
            self.links.append(self.serialise_link(link))

    @staticmethod
    def serialise_doc(doc):
        return {
            'pk': doc.pk,
            'containerid': doc.container.id,
            'created': doc.created.strftime(DATETIME_STRING_FORMAT),
            'updated': doc.updated.strftime(DATETIME_STRING_FORMAT),
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
            'created': link.created.strftime(DATETIME_STRING_FORMAT),
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

    def get_config(self):

        pass
