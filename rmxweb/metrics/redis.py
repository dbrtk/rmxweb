
from redis import ConnectionPool, Redis

from rmxweb.config import (
    METRICS_HOST_NAME, METRICS_DB_NUMBER, METRICS_PASS, METRICS_PORT
)


CONNECTION = None


class RedisConnect(object):

    def __init__(self):

        self.connection = self.get_connection()

    @staticmethod
    def set_connection():
        global CONNECTION
        pool = ConnectionPool(
            password=METRICS_PASS,
            host=METRICS_HOST_NAME,
            port=METRICS_PORT,
            db=METRICS_DB_NUMBER,
        )
        c = Redis(connection_pool=pool)
        if c.ping():
            CONNECTION = c
        else:
            raise RuntimeError(
                f"Redis database ({REDIS_METRICS_DB_HOST}) not available!"
            )

    def get_connection(self):
        if not isinstance(CONNECTION, Redis):
            self.set_connection()
        return CONNECTION

    def get(self, key: str):
        return self.connection.get(key)

    def delete(self, key: str):
        return self.connection.delete(key)

    def set(self, key: str, value: (float, str)):
        return self.connection.set(key, value)
