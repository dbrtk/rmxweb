
import os
import socket


def db_is_ready():
    """Test whether the postgres database is available."""
    try:
        s = socket.create_connection(
            (
                os.environ.get('DATABASE_HOST'),
                os.environ.get('DATABASE_PORT', 5432)
            ), 1
        )
        s.close()
    except socket.timeout:
        print('Postgres is unavailable - sleeping')
        return False
    print('Postgres is up - executing command')
    return True


if __name__ == "__main__":
    if not db_is_ready():
        exit(1)
