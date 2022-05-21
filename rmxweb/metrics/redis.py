
from redis import ConnectionPool, Redis

from rmxweb.config import (
    REDIS_METRICS_DB_HOST, REDIS_METRICS_DB_NUMBER, REDIS_METRICS_DB_PASS,
    REDIS_METRICS_DB_PORT
)


CONNECTION = None


class RedisConnect(object):

    def __init__(self):

        self.connection = self.get_connection()

    @staticmethod
    def set_connection():
        global CONNECTION
        pool = ConnectionPool(
            password=REDIS_METRICS_DB_PASS,
            host=REDIS_METRICS_DB_HOST,
            port=REDIS_METRICS_DB_PORT,
            db=REDIS_METRICS_DB_NUMBER,
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
