""" Models for the container that holds data related to specific crawls.
"""
import datetime
import json
import os
import pytz
import re
import stat
import shutil
from typing import List
import uuid

from django.conf import settings
from django.db import models

from .emit import get_available_features, get_features
from rmxweb import config


class Container(models.Model):

    name = models.CharField(max_length=300, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    crawl_ready = models.BooleanField(default=False)
    container_ready = models.BooleanField(default=False)
    integrity_check_in_progress = models.BooleanField(default=False)

    uid = models.UUIDField(default=uuid.uuid4, unique=True)

    @classmethod
    def get_object(cls, pk: int = None, uid: (str, uuid.UUID) = None):
        """Retrieves an object for a given pk (container id)."""
        obj = None
        if isinstance(pk, int):
            obj = cls.objects.get(pk=pk)
        elif isinstance(uid, (str, uuid.UUID)):
            if isinstance(uid, str):
                uid = uuid.UUID(uid)
            obj = cls.objects.get(uid=uid)
        if not obj:
            raise ValueError(
                f"container with pk: `{pk}` or uid: `{uid}` doesn't exist"
            )
        return obj

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
    def paginate(cls, start: int = 0, end: int = 100):
        """ Paginate containers.
        :param start:
        :param end:
        :return:
        """
        return cls.objects.filter(
            crawl_ready=True, container_ready=True)[start:end + 1]

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

    @property
    def containeruid(self):
        """Returns the container id which is shared across other services while
        crawling, generating matrices, extracting features.
        """
        return self.uid.hex

    def get_dataids(self):
        """Returns the data ids. This method queries the data_set, Data objects
           associated with this container.
        """
        return [_.pk for _ in self.data_set.all()]

    def is_ready(self):
        """ Returns a boolean if the container is ready or not."""
        if not self.integrity_check_in_progress:
            return self.crawl_ready and self.container_ready
        return False

    def set_crawl_ready(self, value: bool = True):
        """Called after starting or finishing the crawl."""
        # todo(): review and delete!
        self.crawl_ready = value
        if value:
            if not self.integrity_check_in_progress:
                self.container_ready = True
        else:
            self.container_ready = False
        self.save()

    def set_integrity_check_in_progress(self):
        """ Set the value of crawl_ready on the container. """
        self.integrity_check_in_progress = True
        self.container_ready = False
        self.save()

    def set_integrity_check_ready(self):
        """Called when a crawl and the integrity check succeed."""
        self.integrity_check_in_progress = False
        if self.crawl_ready:
            self.container_ready = True
        self.save()

    # path and data related methods
    def get_folder_path(self):
        """ Returns the path to the container directory. """
        return os.path.abspath(os.path.normpath(
            os.path.join(
                config.CONTAINER_ROOT, str(self.pk)  # self.uid.hex
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
        Returns the path for the text files in the container.
        :return:
        """
        path = os.path.abspath(os.path.normpath(
            os.path.join(
                self.get_folder_path(), config.TEXT_FOLDER)
            )
        )
        if os.path.isdir(path):
            return path
        return None

    def dataid_fileid(self, data_ids: List[str] = None) -> List[tuple]:
        """Returns a mapping between data ids and file ids."""
        return [
            (_.pk, _.dataid,) for _ in self.data_set.filter(pk__in=data_ids)
        ]

    # feature related methods ==========================================
    # todo(): review these methods. Do we need to return features?

    def features_availability(self, feature_number: int = 10):
        """ Checking feature's availability. """
        status = FeaturesStatus.get_status_feats(
            feats=feature_number, containerid=self.pk)

        out = {
            'requested_features': feature_number,
            'containerid': self.pk,
            'busy': False
        }
        time_zone = pytz.timezone(settings.TIME_ZONE)
        if status:
            if status.busy is True and status.feats == feature_number:
                delta = datetime.datetime.now(time_zone) - status.updated
                delta = divmod(delta.total_seconds(), 60)
                # after 15 minutes, the status lock should be deleted (in case
                # of bugs, crashes).
                if delta[0] >= 15:
                    FeaturesStatus.del_status_feats(
                        feats=feature_number, containerid=self.pk)
                else:
                    out['busy'] = True
        if out['busy'] is False:
            try:
                _count = get_available_features(
                    containerid=self.pk,
                    folder_path=self.get_folder_path())
                next(_ for _ in _count if int(
                    _.get('featcount')) == feature_number)
                _count = list(int(_.get('featcount')) for _ in _count)
            except StopIteration:
                out['available'] = False
            else:
                out['features_count'] = _count
                out['feature_number'] = feature_number
                out['available'] = feature_number in _count
        return out

    def update_on_nlp_callback(self, feats: int = None):
        """ Update the container after nlp finishes computing matrices with
        features.
        :param feats:
        :return:
        """
        # todo(): delete in the close future - FeaturesStatus -> Prometheus
        self.crawl_ready = True
        self.save()
        FeaturesStatus.del_status_feats(feats=feats, containerid=self.pk)

    def get_features_count(self, verbose: bool = False):
        """ Returning the features count. """
        avl = get_available_features(containerid=self.pk,
                                     folder_path=self.get_folder_path())
        if verbose:
            return avl
        else:
            return sorted([int(_.get('featcount')) for _ in avl])

    def get_features(self,
                     feats: int = 10,
                     words: int = 6,
                     docs_per_feat: int = 0,
                     feats_per_doc: int = 3,
                     **_):
        """ Getting the features from nlp. This will call a view method that
            will retrieve or generate the requested data.
        """
        resp = get_features(**{
            'path': self.get_folder_path(),
            'feats': feats,
            'containerid': str(self.pk),
            'words': words,
            'docs_per_feat': docs_per_feat,
            'feats_per_doc': feats_per_doc,
        })
        docs = resp['docs']
        features = resp['features']
        edges = resp['edges']
        words = resp['feature_words']
        data_set = self.data_set.all()
        docs = self.docs_to_json(docs, data_set)
        return {
            'features': features,
            'words': words,
            'docs': docs,
            'edges': edges
        }

    def data_mapping(self):
        """
        :return:
        """
        raise NotImplemented()

    @staticmethod
    def features_to_json(features, data_set):
        """ Mapping a list of given docs to feature's doc. """
        # todo(): delete this method - it duplicates documents.
        for _ftr in features:
            for _doc in _ftr.get('docs'):
                _ = next(_ for _ in data_set if
                         _.dataid == _doc.get('dataid'))
                _doc['title'] = _.title
                _doc['url'] = _.url
        return features

    @staticmethod
    def docs_to_json(docs, data_set):
        """
        """
        for doc in docs:
            _ = next(_ for _ in data_set if _.dataid == doc.get('dataid'))
            doc['url'] = _.url
            doc['title'] = _.title
            doc['pk'] = _.pk
        return docs

    def get_lemma_words(self, lemma: (str, list) = None):
        """For a list of lemma, returns all the words that can be found in
           texts.
        """
        lemma_list = lemma.split(',') if isinstance(lemma, str) else lemma
        if not all(isinstance(_, str) for _ in lemma):
            raise ValueError(lemma)
        pattern = r"""(\{.*(%s).*\})""" % '|'.join(lemma_list)
        with open(self.get_lemma_path(), 'r') as _file:
            content = _file.read()
            dicts = [_[0] for _ in re.findall(pattern, content)]
            return map(json.loads, dicts), lemma_list

    def feature_words(self, feats: int = None):
        """

        :param feats:
        :return:
        """
        pass

    def delete_container(self):
        """
        Deleting the container and its directory on the server.
        :return:
        """
        shutil.rmtree(self.get_folder_path())
        self.delete()


# todo(): get rid of the status model.
class CrawlStatus(models.Model):

    type = models.CharField(max_length=100)
    busy = models.BooleanField(default=False)
    feats = models.IntegerField()
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(max_length=100)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)


# todo(): get rid of the status model. replace it with prometheus
class FeaturesStatus(models.Model):
    """
    Status object used when computing features.
    """
    busy = models.BooleanField(default=False)
    feats = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    containerid = models.IntegerField(null=True)
    computing_dendrogram = models.BooleanField(default=False)

    @classmethod
    def create(cls, containerid: int = None, feats: int = None,
               busy: bool = True):
        """
        :param containerid:
        :param feats:
        :param busy:
        :return:
        """
        obj = cls.get_status_feats(containerid=containerid, feats=feats)
        if obj:
            return obj
        obj = cls(containerid=containerid, feats=feats, busy=busy)
        obj.save()
        return obj

    @classmethod
    def get_status_feats(cls, containerid: int = None, feats: int = None):
        """
        :param containerid:
        :param feats:
        :return:
        """
        try:
            obj = cls.objects.get(containerid=containerid, feats=feats)
        except cls.DoesNotExist as _:
            return None
        return obj

    @classmethod
    def set_status_feats(cls, containerid: int = None, feats: int = None,
                         busy: bool = True):
        """
        :param containerid:
        :param feats:
        :param busy:
        :return:
        """
        obj = cls.get_status_feats(feats=feats, containerid=containerid)
        if obj:
            obj.busy = busy
            obj.save()
        else:
            obj = cls.create(busy=busy, containerid=containerid, feats=feats)
        return obj

    @classmethod
    def del_status_feats(cls, containerid: int = None, feats: int = None):
        """
        :param containerid:
        :param feats:
        :return:
        """
        cls.objects.filter(containerid=containerid, feats=feats).delete()

    @classmethod
    def get_status_dendrogram(cls, containerid):
        """Returns the record for the dendrogram status."""
        try:
            obj = cls.objects.filter(
                containerid=containerid, computing_dendrogram=True)
        except cls.DoesNotExist as _:
            return
        print('getting the status for dendrogram')
        return obj

    @classmethod
    def set_status_dendrogram(cls, containerid):
        """Creating up a record for the process that computes the dendrogram.
        """
        obj = cls.get_status_dendrogram(containerid)
        if obj:
            return obj
        else:
            obj = cls(
                containerid=containerid,
                computing_dendrogram=True,
                busy=True
            )
            obj.save()
        return obj

    @classmethod
    def del_status_dendrogram(cls, containerid):

        cls.objects.filter(
            containerid=containerid, computing_dendrogram=True).delete()

    @classmethod
    def computing_dendrogram_busy(cls, containerid: int = None):
        """Returns true if the dendrogram is currently computed."""
        status = cls.get_status_dendrogram(containerid)
        if status:
            return True
        else:
            return False

    @classmethod
    def computing_feats_busy(cls, containerid: int, feats: int) -> bool:
        """
        :param containerid:
        :param feats:
        :return:
        """
        status = cls.get_status_feats(containerid=containerid, feats=feats)
        if status:
            return True
        else:
            return False

    @classmethod
    def container_busy(cls, containerid: int = None):
        """
        :param containerid:
        :return:
        """
        return cls.objects.filter(containerid=containerid)

    @staticmethod
    def check_timestamp(query_set):

        time_zone = pytz.timezone(settings.TIME_ZONE)
        for record in query_set:
            if (datetime.datetime.now(time_zone) - record.created) > \
                    datetime.timedelta(minutes=15):
                print('THE RECORD SHOULD BE DELETED')
