
import json

from django.db.models import TextField


class ListField(TextField):
    """ Implementation of a list field. """

    def to_python(self, value):
        """

        :return:
        """
        return json.loads(value)


