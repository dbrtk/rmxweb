"""Module that holds queries and fiunction for data retireval. All methods
   return json objects.
"""

import os
import typing

from django.http import Http404

from data.serializers import DatasetSerializer
from data.models import Data
from .decorators import feats_available
from .emit import crawl_async
from .models import Container
from .serializers import ContainerSerializer
from rmxweb.celery import celery
from rmxweb.config import (
    RMXGREP_TASK, DEFAULT_CRAWL_DEPTH, CRAWL_START_MONITOR_COUNTDOWN,
    NLP_TASKS, SCRASYNC_TASKS, RMXWEB_TASKS
)


ERR_MSGS = {
    'container_does_not_exist': 'A container with id: "{}" does not exist.'
}


def paginate(start: int = 0, limit: int = 100):
    """
    Paginates the collection that holds corpora.
    :param start:
    :param limit:
    :return:
    """
    cursor = Container.paginate(start=start, end=limit)
    serializer = ContainerSerializer(cursor, many=True)
    data = serializer.data
    return data


def create_from_crawl(name: str = None, endpoint: str = None,
                      crawl: bool = True):
    """Create a container from a crawl using scrasync."""

    url_list = [endpoint]
    container = Container.create(the_name=name)
    depth = DEFAULT_CRAWL_DEPTH if crawl else 0
    crawlid = crawl_async(
        url_list=url_list, containerid=container.pk, depth=depth)
    return {'success': True, 'containerid': container.pk, 'crawlid': crawlid}


def crawl(containerid: str = None, endpoint: str = None, crawl: bool = True):
    """Launching the crawler (scrasync) on an existing corpus"""
    # todo(): review  - check when its used
    container = Container.get_object(pk=containerid)
    if not container:
        return Http404(f"container with id `{container.pk}` does not exist")
    container.set_crawl_ready(value=False)
    celery.send_task(
        RMXWEB_TASKS['crawl_async'],
        kwargs={
            'url_list': [endpoint],
            'corpus_id': containerid,
            'depth': DEFAULT_CRAWL_DEPTH if crawl else 0
        })

    # crawl_async.delay([endpoint], corpus_id=containerid,
    #                   depth=DEFAULT_CRAWL_DEPTH if crawl else 0)

    return {'success': True, 'containerid': container.pk}


def container_data(containerid):
    """This returns a container data view. It will contain all necesary info
    about a text container.
    """
    obj = {}

    container = Container.get_object(pk=containerid)
    if not container:
        # obj['errors'] = [
        #     ERR_MSGS.get('container_does_not_exist').format(corpusid)
        # ]
        raise RuntimeError(
            ERR_MSGS.get('container_does_not_exist').format(containerid)
        )
    if container.is_ready():
        dataset = DatasetSerializer(container.data_set.all()[:10], many=True)
        obj['available_feats'] = container.get_features_count()
        obj['name'] = container.name
        obj['containerid'] = container.pk
        obj['texts'] = dataset.data
        obj['integrity_check_in_progress'] = \
            container.integrity_check_in_progress
        obj['container_ready'] = container.container_ready
        obj['crawl_ready'] = container.crawl_ready
    else:
        obj['ready'] = False
        obj['status_message'] = \
            "The container and the dataset are not ready yet."

    return obj


def container_is_ready(containerid, feats):
    """Returns an object with information about the state of the container.
    This is called when features are being computed.
    """
    feats = int(feats)
    container = Container.get_object(pk=containerid)
    availability = container.features_availability(feature_number=feats)
    availability.update(dict(features=feats))
    return availability


def crawl_is_ready(containerid):
    """Checking if the crawl is ready in order to load the page. This is called
    when the crawler is running."""
    container = Container.get_object(pk=containerid)
    if not container:
        raise ValueError(containerid)

    if container.crawl_ready and \
            not container.integrity_check_in_progress:
        return {
            'ready': True,
            'containerid': containerid
        }
    return {
        'ready': False,
        'containerid': containerid
    }


def file_upload_ready(containerid):
    """Checks if hte container created from files is ready."""
    # todo(): delete
    container = Container.get_object(pk=containerid)
    if not container:
        raise ValueError(containerid)

    if container.crawl_ready:
        return {
            'ready': True,
            'containerid': containerid
        }
    return {
        'ready': False,
        'containerid': containerid
    }


def texts(containerid):
    """Returns an object that contains texts."""
    container = Container.get_object(pk=containerid)

    obj = {}
    if not container:
        obj['errors'] = [
            ERR_MSGS.get('container_does_not_exist').format(containerid)
        ]
        return obj
    dataset = DatasetSerializer(container.data_set.all(), many=True)
    obj['containerid'] = container.pk
    obj['name'] = container.name
    obj['data'] = dataset.data
    return obj


def delete_texts(containerid: str = None, dataids: typing.List[str] = None):
    """
    Deleting texts from the data set.

    :param containerid:
    :param dataids:
    :return:
    """
    if not all(isinstance(str, _) for _ in dataids):
        raise ValueError(dataids)
    container = Container.get_object(pk=containerid)
    container.set_crawl_ready(value=False)

    celery.send_task(
        RMXWEB_TASKS['delete_many'],
        kwargs={
            'containerid': containerid,
            'data_ids': dataids
        }
    )
    return {'success': True, 'containerid': containerid}


def get_text_file(containerid, dataid):
    """
    Returns the content of a text file in the data-set.
    :param containerid:
    :param dataid:
    :return:
    """
    container = Container.get_object(pk=containerid)

    try:
        doc = Data.get_object(pk=dataid)
    except (ValueError, ):
        return Http404('Requested data and file do not exist.')

    fileid = doc.file_id
    txt = []
    with open(
            os.path.join(container.container_path(), fileid)
    ) as _file:
        for _line in _file.readlines():
            _line = _line.strip()
            if _line:
                txt.append(_line)
    return {
        'text': txt,
        'dataid': dataid,
        'length': len(txt),
        'containerid': container.pk
    }


def lemma_context(containerid, words: typing.List[str] = None):
    """
    Returns the context for lemmatised words. Lemmatised words are the words
    that make a feature - feature-words. The context are all sentences in the
    container that contain one or more feature-word(s).

    :param containerid: the container id
    :param words: these are feature words (lemmatised by default)
    :return:
    """
    container = Container.get_object(pk=containerid)
    if not isinstance(words, list) or \
            not all(isinstance(_, str) for _ in words):
        raise ValueError(words)
    lemma_to_words, lemma = container.get_lemma_words(words)

    matchwords = []
    for i in lemma:
        try:
            mapping = next(_ for _ in lemma_to_words if _.get('lemma') == i)
            matchwords.extend(mapping.get('words'))
        except StopIteration:
            matchwords.append(i)

    data = celery.send_task(
        RMXGREP_TASK['search_text'],
        kwargs={
            'words': matchwords,
            'container_path': container.container_path()
        }).get()
    return {
        'success': True,
        'containerid': container.pk,
        'data': [{'fileid': k, 'sentences': v} for k, v in
                 data.get('data').items()]
    }


@feats_available
def request_features(reqobj):
    """
    Checks for features availability and returns these.
    Retrieving the available features from the nlp. If the features are not
    available, they will be computed along with all necessary matrices and
    objects.

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
    return dict(
        success=True,
        features=features,
        docs=docs
    )
