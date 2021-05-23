

import csv
import typing
import uuid

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





def flatten_features(features: typing.List[typing.Dict]):
    """ Flatten a list of feature objects in order to return an list of words
    and a list of features, that are just placeholders.
    :param features:
    :return:
    """
    feature, word = [], []
    for item in features:
        feat_list = item['features']
        feature.append({
            'count': len(feat_list),
            'id': item['id'],
        })
        for feat_word in feat_list:
            feat_word['id'] = uuid.uuid4().hex
            feat_word['featureid'] = item['id']
            word.append(feat_word)

    return feature, word


class GraphCSV:

    def __init__(self, reqobj: dict):

        self.container = reqobj.get('container')
        del reqobj['container']
        self.features, self.docs = self.container.get_features(**reqobj)
        self.edges = []
        self.feat_nodes = []
        self.data_nodes = []

    def __call__(self):

        self.process_feats()

    def process_feats(self):





    def __call__(self):
        pass



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

    container = reqobj.get('container')
    del reqobj['container']

    features, docs = container.get_features(**reqobj)

    edges, feat_nodes, data_nodes = [], [], []

    for f in features:
        f['id'] = uuid.uuid4().hex
        # todo(): delete!
        # f['group'] = f['id']
        f['type'] = 'feature'
        # cleanup the feat object
        del f['docs']
        feat_nodes.append(f)

    def get_feat(feature):
        for item in feat_nodes:
            if item.get('features') == feature:
                return item
        return None
    for d in docs:
        # _f = get_feat(d['features'][0]['feature'])
        # d['group'] = _f['id']
        d['id'] = uuid.uuid4().hex
        d['type'] = 'document'

        data_nodes.append(d)
        for f in d['features']:
            # if _f and f['feature'] == _f:
            #     the_feat = _f
            # else:
            the_feat = get_feat(f['feature'])
            # _f = None
            if not the_feat:
                if d['features']:
                    raise RuntimeError(f'no feat for doc: {d}')
                else:
                    continue
            edges.append(dict(
                source=d['id'],
                target=the_feat['id'],
                weight=f['weight']
            ))
        # cleanup the doc object
        del d['features']

    feature, word = flatten_features(feat_nodes)

    return {
        'success': True,
        'edge': edges,
        'feature': feature,
        'word': word,
        'document': data_nodes,
        'containerid': container.pk
    }


@feats_available
def graph_to_csv___deppr(reqobj):
    """

    :param reqobj:
    :return:
    """
    container = reqobj.get('container')
    del reqobj['container']

    features, docs = container.get_features(**reqobj)
    nodes = []
    edge, feat_node, feat_words = [], [], []
    for f in features:
        _id = uuid.uuid4().hex

        f['id'] = _id
        f['group'] = _id
        # cleanup the feat object
        del f['docs']
        nodes.append(f)

        f_rec = {
            'id': _id,
            'group': _id
        }
        feat_node.append(f_rec)
        # iterating over feature words
        for w in f['features']:
            w['featureid'] = _id
            w['id'] = uuid.uuid4().hex
            feat_words.append(w)

    def get_feat(feature):
        for item in nodes:
            if item.get('features') == feature:
                return item
        return None
    for d in docs:
        # _f = get_feat(d['features'][0]['feature'])
        # d['group'] = _f['id']
        d['id'] = uuid.uuid4().hex
        for f in d['features']:
            # if _f and f['feature'] == _f:
            #     the_feat = _f
            # else:
            the_feat = get_feat(f['feature'])
            # _f = None
            if not the_feat:
                continue
            edge.append(dict(
                source=d['id'],
                target=the_feat['id'],
                weight=f['weight']
            ))
        # cleanup the doc object
        del d['features']
    return {
        'success': True,
        'edge': edge,
        'feature': feat_node,
        'data': docs,
        'word': feat_words,
        'feature_number': reqobj.get('feats'),
        'containerid': container.pk
    }


class GraphNodesCSV:
    """ Converts a json graph to csv.
    """
    def __init__(self, *args):
        pass


class GraphEdgesCSV:
    """
    """
    pass
