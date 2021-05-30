"""A serialiser for search text and context."""
from copy import deepcopy

from .csv_serialiser import CsvSerialiser
from .serialiser_factory import SerialiserFactory

TEXT_COLUMNS = ['dataid', 'text']
DATA_COLUMNS = ['dataid', 'pk', 'title', 'url', 'created']

CONFIG = {
    'columns': {
        'text': TEXT_COLUMNS,
        'docs': DATA_COLUMNS,
    },
    'data_type_mapping': {
        'text': {
            'dataid': 'string',
            'text': 'string'
        },
        'docs': {
            'dataid': 'string',
            'pk': 'integer',
            'url': 'string',
            'title': 'string',
            'created': 'datetime'
        },
    }
}


@SerialiserFactory.set_serialiser('search_text_csv')
class SearchTextCsv(CsvSerialiser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = self.data.pop('response')
        self.docs = self.data.pop('docs')

        self.text = self.response.pop('data')
        self.lemma = self.data.pop('lemma')
        self.words = self.response.pop('words')

        del self.data

        self.write_to_zip(
            self.get_docs(),
            self.get_conf(),
            self.get_text()
        )

    def get_text(self):
        return self.to_csv(
            rows=self.docs,
            file_name='docs.csv',
            columns=DATA_COLUMNS)

    def get_docs(self):
        return self.to_csv(
            rows=self.text,
            file_name='text.csv',
            columns=TEXT_COLUMNS)

    def get_conf(self):
        out = deepcopy(CONFIG)
        out['count'] = {
            'docs': len(self.docs),
            'text': len(self.text)
        }
        out['lexemes'] = self.lemma
        out['search-words'] = self.words
        return self.to_json(out, 'config.json')
