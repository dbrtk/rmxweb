
import abc
import io
import json
import typing
import zipfile


class Serialiser(abc.ABC):
    """
    Converting lists of python dicts to csv datasets and writing these to
    zipfile.
    """
    def __init__(self, data: (dict, list) = None):
        """
        A serialiser expects a dataset as input called `data`.
        :param data:
        """
        self.zip = io.BytesIO()
        self.data = data

    def write_to_zip(self, *files):
        """
        :param files:
        :return:
        """
        with zipfile.ZipFile(
                self.zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in files:
                zf.writestr(item['name'], item['file'].getvalue())

    @staticmethod
    def to_json(obj: typing.Dict, file_name: str):
        """

        :param obj:
        :param file_name:
        :return:
        """
        _file = io.StringIO()
        json.dump(obj, _file, indent=4, separators=(',', ': '))
        return {
            'name': file_name,
            'file': _file
        }

    @abc.abstractmethod
    def get_value(self):

        raise NotImplementedError('get_value needs to be implemented')
