#!/bin/sh

set -e

until PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -U "$DATABASE_USERNAME" -d "$DATABASE_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

>&2 echo "Running manage.py migrate"
python3 manage.py migrate

>&2 echo "Removing postgresql"
apt-get -y purge postgres* && apt-get -y autoclean && apt-get -y autoremove

>&2 echo "Running the app with gunicorn"
gunicorn rmxweb.wsgi:application --bind 0.0.0.0:8000

