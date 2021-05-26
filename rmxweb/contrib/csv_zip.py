
import abc
import csv
import io
import typing
import zipfile


class CsvZip(abc.ABC):
    """
    Converting lists of python dicts to csv datasets and writing these to
    zipfile.
    """
    def __init__(self):

        self.zip = io.BytesIO()

    @staticmethod
    def to_csv(rows: typing.List,
               file_name: str,
               columns: typing.List[str]):
        """Convert a list of objects to a csv file."""
        _file = io.StringIO()
        writer = csv.DictWriter(_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        return {
            'name': file_name,
            'file': _file,
        }

    def write_to_zip(self, *files):
        """
        :param files:
        :return:
        """
        with zipfile.ZipFile(
                self.zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in files:
                zf.writestr(item['name'], item['file'].getvalue())

    def get_zip(self): return self.zip.getvalue()


