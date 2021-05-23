

import csv
import io
import typing
import uuid
import zipfile

from container.decorators import feats_available


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


class GraphCSV:

    EDGE_COLUMNS = ['source', 'target', 'weight']
    FEAT_COLUMNS = ['id', 'count']
    DATA_COLUMNS = ['id', 'dataid', 'url', 'title', 'fileid']
    WORD_COLUMNS = ['id', 'word', 'weight', 'featureid']

    def __init__(self, reqobj: dict):

        self.container = reqobj.get('container')
        del reqobj['container']
        print('get_features')
        self.features, self.docs = self.container.get_features(**reqobj)
        print('features and docs returned')

        self.feat_nodes = []

        self.edge = []
        self.data = []
        self.feature = []
        self.word = []

    def __call__(self):
        print('iter feats')
        self.iter_feats()
        print('iter docs')
        self.iter_docs()
        print('flatten feats')
        self.flatten_features()
        return

    def find_feat(self, feature):

        for item in self.feat_nodes:
            if item.get('features') == feature:
                return item
        return None

    def iter_feats(self):

        while self.features:
            f = self.features.pop(0)
            f['id'] = uuid.uuid4().hex
            print(f'the feat: {f}')
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

    @staticmethod
    def to_csv(rows: typing.List,
               file_name: str,
               columns: typing.List[str]):

        _file = io.StringIO()
        writer = csv.DictWriter(_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        return {
            'name': file_name,
            'file': _file,
        }

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
    memf = io.BytesIO()
    with zipfile.ZipFile(
            memf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write()


    import pdb ; pdb.set_trace()

