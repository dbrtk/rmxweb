from .serialiser_factory import SerialiserFactory
from .csv_serialiser import CsvSerialiser
from rmxweb.config import DATETIME_STRING_FORMAT


LINK_COLUMNS = ['pk', 'created', 'url', 'hostname', 'dataid']
DOC_COLUMNS = [
    'pk', 'containerid', 'created', 'updated', 'url', 'hostname', 'seed',
    'title', 'file_id', 'hash_text'
]


@SerialiserFactory.set_serialiser('data_list_csv')
class DataListCsv(CsvSerialiser):

    def __init__(self, *args, **kwargs):

        super(DataListCsv, self).__init__(*args, **kwargs)
        self.docs = []
        self.links = []
        self.iter_docs()
        self.iter_links()
        self.write_to_zip(
            self.get_links(),
            self.get_docs()
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
