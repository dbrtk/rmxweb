""" Models for the container that holds data related to specific crawls.
"""

from django.core.validators import URLValidator
from django.db import models


class Container(models.Model):

    name = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    crawl_ready = models.BooleanField(default=False)
    integrity_check_in_progress = models.BooleanField(default=False)


class Url(models.Model):

    url = models.TextField(validators=[URLValidator])
    created = models.DateTimeField(auto_now_add=True)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)


class DataObject(models.Model):
    """
    structure = {
        'data_id': str,
        'file_id': str,  # this is a string representation of a uuid

        # todo(): delete
        'file_path': str,

        'texthash': str,
        'file_hash': str,

        'title': str,
        'file_name': str,

        'url': str,
        'text_url': str,

        'checked': bool,
    }
    """

    # todo(): review and delete this model! It replicates the data object.

    container = models.ForeignKey(Container, on_delete=models.CASCADE)

    data_id = models.IntegerField()
    file_id = models.CharField(max_length=100)
    file_path = models.CharField(max_length=300)
    title = models.TextField()
    file_name = models.CharField(max_length=300)

    url = models.TextField(validators=[URLValidator])
    text_url = models.TextField()
    checked = models.BooleanField(default=False)


class CrawlStatus(models.Model):

    type = models.CharField(max_length=100)
    busy = models.BooleanField(default=False)
    feats = models.IntegerField()
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(max_length=100)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)


def insert_urlobj(containerid: int = None, url_obj: dict = None):
    """ Validating the url object and inserting it in the container list of urls.
    """
    DataObject.simple_validation(url_obj)

    containerid = bson.ObjectId(containerid)
    _COLLECTION.update_one(
        {'_id': containerid},
        {'$push': {'urls': url_obj}}
    )
    return containerid


def set_crawl_ready(containerid, value):
    """ Set the value of crawl_ready on the container. """
    _id = bson.ObjectId(containerid)
    if not isinstance(value, bool):
        raise RuntimeError(value)
    return _COLLECTION.update({'_id': _id}, {'$set': {'crawl_ready': value}})


def set_integrity_check_in_progress(containerid, value):
    """ Set the value of crawl_ready on the container. """
    _id = bson.ObjectId(containerid)
    if not isinstance(value, bool):
        raise RuntimeError(value)
    return _COLLECTION.update({'_id': _id}, {
        '$set': {'integrity_check_in_progress': value}})


def integrity_check_ready(containerid):
    """Called when a crawl and the integrity check succeed."""
    return _COLLECTION.update({'_id': bson.ObjectId(containerid)}, {
        '$set': {
            'integrity_check_in_progress': False,
            'crawl_ready': True,
            'corpus_ready': True
        }})


def container_status(containerid):
    """Retrieves status related data for a container id."""
    return _COLLECTION.find_one({'_id': bson.ObjectId(containerid)}, {
        'crawl_ready': 1,
        'integrity_check_in_progress': 1,
        'corpus_ready': 1,
        'data_from_files': 1,
        'data_from_the_web': 1,
    })


def request_availability(containerid, reqobj: dict, container=None):
    """ Checks for the availability of a feature.
    The reqobj should look like this:
    {
        public: 'bool - if true, send this message to the group',
        features: 'the number of features',
        words: 'the number of feature words',
        documents: 'the number of documents per feature'
    }
    """
    structure = dict(
        features=int
    )
    for k, v in reqobj.items():
        if not isinstance(v, structure.get(k)):
            raise ValueError(reqobj)

    container = container or ContainerModel.inst_by_id(containerid)

    availability = container.features_availability(
        feature_number=reqobj['features'])

    return availability
