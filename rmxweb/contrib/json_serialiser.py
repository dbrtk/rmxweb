
import json

from .serialiser import Serialiser


class JsonSerialiser(Serialiser):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.json = None
        self.make_json()

    def make_json(self):

        self.json = json.dumps(self.data)

    def get_value(self): return self.json
