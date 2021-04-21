""" Models for the container that holds data related to specific crawls.
"""

import os
import uuid

from django.db import models

from rmxweb import config


class Container(models.Model):

    name = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    crawl_ready = models.BooleanField(default=False)
    container_ready = models.BooleanField(default=False)
    integrity_check_in_progress = models.BooleanField(default=False)

    uid = models.UUIDField(default=uuid.uuid4)

    @classmethod
    def get_object(cls, pk):
        """Retrieves an object for a given pk (container id)."""
        obj = cls.objects.get(pk=pk)
        if not obj:
            raise
        return obj

    @classmethod
    def inst_by_id(cls, pk: int = None): return cls.get_object(pk)

    @classmethod
    def set_crawl_ready(cls, containerid, value: bool = None):
        """ Set the value of crawl_ready on the container. """
        if not isinstance(value, bool):
            raise RuntimeError(value)
        obj = cls.get_object(containerid)
        obj.crawl_ready = value
        return obj.save()

    @classmethod
    def set_integrity_check_in_progress(cls, containerid, value: bool = None):
        """ Set the value of crawl_ready on the container. """
        if not isinstance(value, bool):
            raise RuntimeError(value)
        obj = cls.get_object(containerid)
        obj.integrity_check_in_progress = value
        obj.save()
        return obj

    @classmethod
    def integrity_check_ready(cls, containerid):
        """Called when a crawl and the integrity check succeed."""
        obj = cls.get_object(containerid)
        obj.integrity_check_in_progress = False
        obj.crawl_ready = True
        obj.container_ready = True
        return obj.save()

    def container_status(self):
        """Retrieves status related data for a container id."""
        return {
            'crawl_ready': self.crawl_ready,
            'integrity_check_in_progress': self.integrity_check_in_progress,
            'corpus_ready': self.container_ready,
        }

    def get_dataids(self):
        """Returns the data ids"""
        return [_.pk for _ in self.data_set.all()]

    # path and data related methods
    def get_folder_path(self):
        """ Returns the path to the container directory. """
        return os.path.abspath(os.path.normpath(
            os.path.join(
                config.CONTAINER_ROOT, self.uid
            )
        ))

    def get_vectors_path(self):
        """ Returns the path of the file that contains the vectors. """
        return os.path.join(self.matrix_path, 'vectors.npy')

    @property
    def matrix_path(self):
        return os.path.join(self.get_folder_path(), config.MATRIX_FOLDER)

    @property
    def matrix_exists(self):
        """Returns True is the matix directory with its files exists."""
        return os.path.exists(self.matrix_path) and os.listdir(
            self.matrix_path)

    @property
    def wf_path(self): return os.path.join(self.matrix_path, 'wf')

    def get_lemma_path(self):
        """Returns the path to the json file that contains the mapping between
           lemma and words, as these appear in texts.
        """
        path = os.path.join(self.matrix_path, 'lemma.json')
        if not os.path.isfile(path):
            raise RuntimeError(path)
        return path


class CrawlStatus(models.Model):

    type = models.CharField(max_length=100)
    busy = models.BooleanField(default=False)
    feats = models.IntegerField()
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(max_length=100)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)


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

    container = container or Container.objects.get(pk=containerid)
    availability = container.features_availability(
        feature_number=reqobj['features'])
    return availability
