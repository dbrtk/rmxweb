""" Models for the Data Objects. """

import hashlib
import os
import stat
import uuid

from django.db import models
from django.conf import settings

from .errors import DuplicateUrlError
from rmxweb.container.models import Container


class Data(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    container = models.ForeignKey(Container, on_delete=models.CASCADE)

    # hostname = models.CharField(max_length=200)

    # these fields were saved on the data object of the container.
    data_id = models.IntegerField()
    file_id = models.CharField(max_length=100)
    file_path = models.CharField(max_length=300)
    title = models.TextField()
    hash_text = models.CharField(max_length=50)

    # file_name = models.CharField(max_length=300)
    # text_url = models.TextField()
    # checked = models.BooleanField(default=False)

    @classmethod
    def create(
            cls,
            data: (str, list,) = None,
            container_id: int = None,
            links: list = None,
            title: str = None,
            endpoint: str = None):
        """
        Create and save a Data object with all the urls that make it.

        :param data:
        :param container_id:
        :param links:
        :param title:
        :param endpoint:
        :return:
        """
        container_obj = Container.objects.get(pk=container_id)
        if not container_obj:
            raise RuntimeError(container_id)

        container_files_path = container_path(container_id)
        obj = cls(title=title, contianer=container_obj)
        _pk = obj.save()

        endpoint_obj = Link(url=endpoint, data=obj, seed=True)
        endpoint_obj.save()
        for item in links:
            _ = Link(url=item, data=obj).save()
        try:
            file_id, hashtext = obj.write_data_to_file(
                path=container_files_path,
                file_id=obj.file_identifier(),
                data=data
            )
        except DuplicateUrlError as _:
            return None
        else:
            obj.file_id = file_id
            obj.hash_text = hashtext
        obj.save()
        return obj

    def write_data_to_file(self, path, data, file_id: str = None) -> (str, str):
        """ Writing data into a file in the container folder. """

        path = os.path.normpath(os.path.join(path, file_id))

        if os.path.isfile(path):
            raise DuplicateUrlError
        self.save()
        hasher = hashlib.md5()

        with open(path, 'a+') as _file:
            for txt in data:
                hasher.update(bytes(txt, 'utf-8'))
                _file.write(txt)
                _file.write('\n\n')

        # permissions 'read, write, execute' to user, group, other (777)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        return file_id, hasher.hexdigest()

    def file_identifier(self):
        """Generating a unique id for the file name."""
        return uuid.uuid4().hex


class Link(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=500)
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    seed = models.BooleanField(default=False)


def create_data_obj(container_id: int = None,
                    url: str = None):

    contr = Container.objects.get(pk=container_id)
    if not contr:
        raise RuntimeError(container_id)

    data_obj = Data(container=contr, url=url, )
    data_obj.save()


def container_path(container_id: str = None):
    """ Returns the path for the files in the container. """
    path = os.path.abspath(os.path.normpath(
        os.path.join(
            settings.CONTAINER_ROOT, container_id, settings.TEXT_FOLDER)
        )
    )
    if os.path.isdir(path):
        return path
    return None
