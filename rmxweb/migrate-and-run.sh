#!/bin/sh

set -e

until python3 check_db_availability.py; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

>&2 echo "Running manage.py migrate"
python3 manage.py migrate

>&2 echo "Running the app with gunicorn"
gunicorn rmxweb.wsgi:application --bind 0.0.0.0:8000

