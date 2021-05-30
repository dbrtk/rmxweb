
import csv
import io
import typing

from . serialiser import Serialiser


class CsvSerialiser(Serialiser):
    """
    Converting lists of python dicts to csv datasets and writing these to
    zipfile.
    """
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

    def get_value(self): return self.zip.getvalue()
