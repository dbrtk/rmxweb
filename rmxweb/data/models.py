""" Models for the Data Objects. """

import hashlib
import os
import stat
import typing
import urllib.parse
import uuid

from django.db import models
from django.core import validators
from .errors import DuplicateUrlError
from container.models import Container
from rmxweb import config


class Data(models.Model):
    """ The Data model holds the information related to the url and the data
    file on the server.
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    container = models.ForeignKey(Container, on_delete=models.CASCADE)

    url = models.TextField(validators=[validators.URLValidator()], null=True)
    hostname = models.CharField(max_length=500, null=True)

    # if True the data object is a crawl seed
    seed = models.BooleanField(default=False)

    # these fields were saved on the data object of the container.
    file_id = models.UUIDField(default=uuid.uuid4, editable=False)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    title = models.TextField(blank=True, null=True)

    hash_text = models.CharField(
        max_length=config.HEXDIGEST_SIZE, blank=True, null=True)

    # todo(): review the link field.
    # links = UrlListField()

    # file_name = models.CharField(max_length=300)
    # text_url = models.TextField()
    # checked = models.BooleanField(default=False)

    @classmethod
    def get_object(cls, pk: int = None):
        """Retrieves an object for a given pk."""
        try:
            obj = cls.objects.get(pk=pk)
        except cls.DoesNotExist as _:
            raise ValueError(
                f"Data object with pk: `{pk}` doesn't exist."
            )
        return obj

    @classmethod
    def create(
            cls,
            data: (str, list,) = None,
            containerid: int = None,
            links: list = None,
            title: str = None,
            endpoint: str = None,
            seed: bool = False):
        """
        Create and save a Data object with all the urls that make it.

        :param data:
        :param containerid:
        :param links:
        :param title:
        :param endpoint:
        :param seed:
        :return:
        """
        container_obj = Container.get_object(containerid)
        url_parse = urllib.parse.urlparse(endpoint)
        obj = cls(title=title,
                  container=container_obj,
                  url=endpoint,
                  seed=seed,
                  hostname=url_parse.hostname)

        file_path = obj.get_file_path(container=container_obj)
        obj.file_path = file_path
        try:
            hash_text = obj.write_data_to_file(
                path=file_path,
                data=data
            )
        except DuplicateUrlError as _:
            return None
        else:
            obj.hash_text = hash_text
        obj.save()
        for item in links:
            Link.create(url=item, data=obj)
        return obj

    @classmethod
    def filter_seed_data(cls, cids: typing.List[int]):
        """
        Filters all seed data objects for a list of container ids.
        :param cids: list of container ids.
        :return:
        """
        return cls.objects.filter(seed=True, container_id__in=cids)

    def get_file_path(self, container: Container = None):
        """
        Returns the path of the file as it is saved on disk
        :return:
        """
        containerid = self.container.pk
        if not container:
            container = Container.get_object(containerid)

        return os.path.normpath(
            os.path.join(container.container_path(), self.dataid)
        )

    def write_data_to_file(self, path, data) -> (str, str):
        """ Writing data into a file in the container folder. """

        if os.path.isfile(path):
            raise DuplicateUrlError(path)
        self.save()
        hash = hashlib.blake2b(digest_size=config.DIGEST_SIZE)

        with open(path, 'a+') as _file:
            for txt in data:
                hash.update(bytes(txt, 'utf-8'))
                _file.write(txt)
                _file.write('\n\n')
        # permissions 'read, write, execute' to user, group, other (777)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        return hash.hexdigest()

    def get_all_links(self):
        """Returns all the links for a given container id."""
        return self.link_set.all()

    def get_text(self):
        """Retrieves the text from the file save don disk.
        :return:
        """
        out = []
        with open(self.get_file_path(), 'r') as _file:
            for line in _file.readlines():
                out.append(line)
        return out

    @classmethod
    def delete_many(cls, data_ids: typing.List[int], containerid: int = None):
        """
        Delete many objects for a given containerid and a list of data ids.
        :param data_ids:
        :param containerid:
        :return:
        """
        container = Container.get_object(pk=containerid)
        for obj in cls.objects.filter(pk__in=data_ids):
            if container != obj.container:
                continue
            _path = obj.file_path
            if os.path.exists(_path):
                os.remove(_path)
            obj.delete()

    @property
    def dataid(self):
        """Returns the file_id as a hex string."""
        return self.file_id.hex


class Link(models.Model):
    """ Model for every link that appears in a web page (Data model). """
    created = models.DateTimeField(auto_now_add=True)
    url = models.TextField(validators=[validators.URLValidator()], null=True)
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=500, null=True)

    @classmethod
    def create(cls, url: str = None, data: Data = None):
        """ Creating a Link object.
        :param url:
        :param data:
        :return:
        """
        cls(url=url,
            hostname=urllib.parse.urlparse(url).hostname,
            data=data).save()


def create_data_obj(container_id: int = None,
                    url: str = None):

    contr = Container.objects.get(containerid=container_id)
    if not contr:
        raise RuntimeError(container_id)

    data_obj = Data(container=contr, url=url, )
    data_obj.save()
