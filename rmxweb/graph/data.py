

import csv
import io
import typing
import uuid
import zipfile

from container.decorators import feats_available
from contrib.csv_zip import CsvZip


@feats_available
def graph(reqobj):
    """
    Retrieving data (links and nodes) for a force-directed graph. This function
    maps the documents and features to links and nodes.

    these parameters are expected by the decorator:
    containerid: int = None,
    words: int = 10,
    features: int = 10,
    docsperfeat: int = 5,
    featsperdoc: int = 3

    :param reqobj:
    :return:
    """

    container = reqobj.get('container')
    del reqobj['container']

    features, docs = container.get_features(**reqobj)

    links, nodes = [], []

    for f in features:
        f['id'] = uuid.uuid4().hex
        f['group'] = f['id']
        f['type'] = 'feature'
        # cleanup the feat object
        del f['docs']
        nodes.append(f)

    def get_feat(feature):
        for item in nodes:
            if item.get('features') == feature:
                return item
        return None
    for d in docs:
        _f = get_feat(d['features'][0]['feature'])
        d['group'] = _f['id']
        d['id'] = uuid.uuid4().hex
        d['type'] = 'document'

        nodes.append(d)
        for f in d['features']:
            if _f and f['feature'] == _f:
                the_feat = _f
            else:
                the_feat = get_feat(f['feature'])
            _f = None
            if not the_feat:
                if d['features']:
                    raise RuntimeError(f'no feat for doc: {d}')
                else:
                    continue
            links.append(dict(
                source=d['id'],
                target=the_feat['id'],
                weight=f['weight']
            ))
        # cleanup the doc object
        del d['features']
    return {
        'success': True,
        'edge': links,
        'node': nodes,
        'features': reqobj.get('feats'),
        'containerid': container.pk
    }


class GraphCSV(CsvZip):

    EDGE_COLUMNS = ['source', 'target', 'weight']
    FEAT_COLUMNS = ['id', 'count']
    DATA_COLUMNS = ['id', 'dataid', 'url', 'title', 'fileid']
    WORD_COLUMNS = ['id', 'word', 'weight', 'featureid']

    def __init__(self, reqobj: dict):

        super().__init__()

        self.container = reqobj.get('container')
        del reqobj['container']
        self.features, self.docs = self.container.get_features(**reqobj)

        self.feat_nodes = []

        self.edge = []
        self.data = []
        self.feature = []
        self.word = []

    def __call__(self):

        self.iter_feats()

        self.iter_docs()

        self.flatten_features()

        self.write_to_zip(
            self.get_feat(),
            self.get_data(),
            self.get_edge(),
            self.get_word()
        )

    def find_feat(self, feature):

        for item in self.feat_nodes:
            if item.get('features') == feature:
                return item
        return None

    def iter_feats(self):

        while self.features:
            f = self.features.pop(0)
            f['id'] = uuid.uuid4().hex

            # cleanup the feat object
            del f['docs']
            self.feat_nodes.append(f)

    def iter_docs(self):

        while self.docs:
            d = self.docs.pop(0)
            d['id'] = uuid.uuid4().hex
            self.data.append(d)
            for f in d['features']:
                the_feat = self.find_feat(f['feature'])
                if not the_feat:
                    if d['features']:
                        raise RuntimeError(f'no feat for doc: {d}')
                    else:
                        continue
                self.edge.append(dict(
                    source=d['id'],
                    target=the_feat['id'],
                    weight=f['weight']
                ))
            del d['features']

    def flatten_features(self):
        """ Flatten a list of feature objects in order to return an list of
        words and a list of features, that are just placeholders.
        :return:
        """
        while self.feat_nodes:
            item = self.feat_nodes.pop(0)
            feat_list = item['features']
            self.feature.append({
                'count': len(feat_list),
                'id': item['id'],
            })
            for feat_word in feat_list:
                feat_word['id'] = uuid.uuid4().hex
                feat_word['featureid'] = item['id']
                self.word.append(feat_word)

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

    def config(self):

        out = {
            'columns': {
                'edge': self.EDGE_COLUMNS,
                'feat': self.FEAT_COLUMNS,
                'word': self.WORD_COLUMNS,
                'data': self.DATA_COLUMNS,
            },
        }


@feats_available
def graph_to_csv(reqobj):
    """
    Retrieving data (links and nodes) for a force-directed graph. This function
    maps the documents and features to links and nodes.

    these parameters are expected by the decorator:
    containerid: int = None,
    words: int = 10,
    features: int = 10,
    docsperfeat: int = 5,
    featsperdoc: int = 3

    :param reqobj:
    :return:
    """
    obj = GraphCSV(reqobj)
    obj()
    return obj
