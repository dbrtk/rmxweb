
from .serialiser import Serialiser


class SerialiserFactory:
    serialisers = {}

    @classmethod
    def set_serialiser(cls, serialiser_name: str):
        """

        :param serialiser_name:
        :return:
        """

        def wrapper(serialiser):

            if serialiser_name not in cls.serialisers:
                cls.serialisers[serialiser_name] = serialiser
            else:
                pass
            return serialiser

        return wrapper

    def register_serialiser(
            self, serialiser_name: str, serialiser: Serialiser):
        """
        Registers new serialisers.
        :param serialiser_name:
        :param serialiser:
        :return:
        """

        if serialiser_name not in self.serialisers:
            self.serialisers[serialiser_name] = serialiser
        else:
            pass
        return serialiser

    def get_serialiser(self, serialiser_name: str):
        """
        Returns a serialiser class for a given serialiser name.
        :param serialiser_name:
        :return:
        """
        if serialiser_name not in self.serialisers:
            raise ValueError(
                f'{serialiser_name} is not defined in serialisers.'
            )
        return self.serialisers[serialiser_name]


# factory = SerialiserFactory()
