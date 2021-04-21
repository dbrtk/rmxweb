
import json

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import TextField


class UrlListField(TextField):
    """ Implementation of a list field that contains valid urls. """

    def to_python(self, value):
        """
        Loads the string value to a python object; a list of strings.
        :return:
        """
        return json.loads(value)

    def value_to_string(self, obj):
        """
        Makes a list of urls into a string that can be saved in the database.
        This function does the validation of the object (list) and all of the
        items it contains.
        :param obj:
        :return:
        """
        if not isinstance(obj, list):
            raise ValueError(obj)
        validate = URLValidator()
        for url in obj:
            try:
                validate(url)
            except ValidationError as _:
                raise ValueError(url)
        return json.dumps(obj)
