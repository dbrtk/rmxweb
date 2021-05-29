

class SerialiserFactory:

    serialisers = {}

    @classmethod
    def set_serialiser(cls, serialiser_name: str):
        """

        :param serialiser_name:
        :return:
        """

        print(f'set serialiser: {serialiser_name}')

        def wrapper(serialiser):

            print(f'serialiser object: {serialiser}')
            if serialiser_name not in cls.serialisers:
                cls.serialisers[serialiser_name] = serialiser
            else:
                pass
            return serialiser
        return wrapper

    def get_serialiser(self, serialiser_name: str):

        if serialiser_name not in self.serialisers:
            raise ValueError(
                f'{serialiser_name} is not defined in serialisers.'
            )
        return self.serialisers[serialiser_name]


