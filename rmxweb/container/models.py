""" Models for the container that holds data related to specific crawls.
"""

import datetime
import os
import stat
import uuid

from django.db import models

from .emit import get_available_features
from rmxweb import config


class Container(models.Model):

    name = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    crawl_ready = models.BooleanField(default=False)
    container_ready = models.BooleanField(default=False)
    integrity_check_in_progress = models.BooleanField(default=False)

    uid = models.UUIDField(default=uuid.uuid4, unique=True)

    @classmethod
    def get_object(cls, pk):
        """Retrieves an object for a given pk (container id)."""
        obj = cls.objects.get(pk=pk)
        if not obj:
            raise ValueError(f"container with pk: `{pk}` doesn't exist")
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

    @classmethod
    def create(cls, the_name: str = None):
        """
        Creating a new container object and a directory that will hold the
        files: texts, matrices, pickles...
        :param the_name:
        :return:
        """
        obj = cls(name=the_name)
        obj.save()
        obj.create_folder()
        return obj

    @classmethod
    def container_status(cls, pk: int = None):
        """Retrieves status related data for a container id."""
        obj = cls.get_object(pk=pk)
        return {
            'crawl_ready': obj.crawl_ready,
            'integrity_check_in_progress': obj.integrity_check_in_progress,
            'container_ready': obj.container_ready,
        }

    @classmethod
    def request_availability(cls, containerid, reqobj: dict, container=None):
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

        container = container or cls.objects.get(pk=containerid)
        availability = container.features_availability(
            feature_number=reqobj['features'])
        return availability

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

    def get_dataids(self):
        """Returns the data ids. This method queries the data_set, Data objects
           associated with this container.
        """
        return [_.pk for _ in self.data_set.all()]

    # path and data related methods
    def get_folder_path(self):
        """ Returns the path to the container directory. """
        if not isinstance(self.pk, int):
            raise RuntimeError(self)
        return os.path.abspath(os.path.normpath(
            os.path.join(
                config.CONTAINER_ROOT, str(self.pk)  # uid.hex
            )
        ))

    def get_vectors_path(self):
        """ Returns the path of the file that contains the vectors. """
        return os.path.join(self.matrix_path, 'vectors.npy')

    def get_lemma_path(self):
        """Returns the path to the json file that contains the mapping between
           lemma and words, as these appear in texts.
        """
        path = os.path.join(self.matrix_path, 'lemma.json')
        if not os.path.isfile(path):
            raise RuntimeError(path)
        return path

    def create_folder(self):
        """ Creating the directory for the texts and matrices.

            permissions 'read, write, execute' to user, group and
            other (777).
        """
        # (_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
        path = self.get_folder_path()
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=False)
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        for _path in [os.path.join(path, config.MATRIX_FOLDER),
                      os.path.join(path, config.TEXT_FOLDER)]:
            if not os.path.isdir(_path):
                os.makedirs(_path, exist_ok=False)
                os.chmod(_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        return path

    def get_container_id(self): return self.uid

    def container_path(self):
        """
        Returns the path for the files in the container.
        :return:
        """
        path = os.path.abspath(os.path.normpath(
            os.path.join(
                config.CONTAINER_ROOT, str(self.pk), config.TEXT_FOLDER)
            )
        )
        if os.path.isdir(path):
            return path
        return None


    # def features_availability(self, feature_number: int = 10):
    #     """ Checking feature's availability. """
    #     status = self.get_status_feats(feats=feature_number)
    #
    #     out = {
    #         'requested_features': feature_number,
    #         'corpusid': self.pk,
    #         'busy': False
    #     }
    #     if status:
    #         if status.get('busy') is True and status.get(
    #                 'feats') == feature_number:
    #             delta = datetime.datetime.now() - status.get('updated')
    #             delta = divmod(delta.total_seconds(), 60)
    #             # after 15 minutes, the status lock should be deleted (in case
    #             # of bugs, crashes).
    #             if delta[0] >= 15:
    #                 self.del_status_feats(feats=feature_number)
    #             else:
    #                 out['busy'] = True
    #     if out['busy'] is False:
    #         try:
    #             _count = get_available_features(
    #                 containerid=str(self.get_id()),
    #                 folder_path=self.get_folder_path())
    #             next(_ for _ in _count if int(
    #                 _.get('featcount')) == feature_number)
    #             _count = list(int(_.get('featcount')) for _ in _count)
    #         except StopIteration:
    #             out['available'] = False
    #         else:
    #             out['features_count'] = _count
    #             out['feature_number'] = feature_number
    #             out['available'] = feature_number in _count
    #     return out


class CrawlStatus(models.Model):

    type = models.CharField(max_length=100)
    busy = models.BooleanField(default=False)
    feats = models.IntegerField()
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(max_length=100)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)


