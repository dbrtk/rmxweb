""" Models for the Data Objects. """

import hashlib
import os
import stat
import urllib.parse
import uuid

from django.db import models

from .errors import DuplicateUrlError
from container.models import Container
from rmxweb import config


class Data(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    container = models.ForeignKey(Container, on_delete=models.CASCADE)

    url = models.URLField(null=True)
    hostname = models.CharField(max_length=200, null=True)

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
    def create(
            cls,
            data: (str, list,) = None,
            containerid: int = None,
            links: list = None,
            title: str = None,
            endpoint: str = None):
        """
        Create and save a Data object with all the urls that make it.

        :param data:
        :param containerid:
        :param links:
        :param title:
        :param endpoint:
        :return:
        """
        container_obj = Container.get_object(containerid)
        url_parse = urllib.parse.urlparse(endpoint)
        obj = cls(title=title,
                  container=container_obj,
                  url=endpoint,
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

    def get_file_path(self, containerid: str = None,
                      container: Container = None):
        """
        Returns the path of the file as it is saved on disk
        :return:
        """
        if not container:
            container = Container.get_object(containerid)

        return os.path.normpath(
            os.path.join(container.container_path(), self.file_id.hex)
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


class Link(models.Model):
    """ Model for every link that appears in a web page (Data model). """
    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=500)
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=200, null=True)

    @classmethod
    def create(cls, url: str = None, data: Data = None):
        """ Creating a Link object.
        :param url:
        :param data:
        :return:
        """
        url = urllib.parse.urlparse(url)
        cls(url=url, hostname=url.hostname, data=data).save()


def create_data_obj(container_id: int = None,
                    url: str = None):

    contr = Container.objects.get(pk=container_id)
    if not contr:
        raise RuntimeError(container_id)

    data_obj = Data(container=contr, url=url, )
    data_obj.save()
