
import json

from .serialiser import Serialiser


class JsonSerialiser(Serialiser):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def get_value(self): return self.data
