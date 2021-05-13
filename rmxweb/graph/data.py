

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
