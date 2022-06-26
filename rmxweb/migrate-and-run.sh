#!/bin/sh

set -e

>&2 echo "Running manage.py migrate"
python3 manage.py migrate

>&2 echo "Running the app with gunicorn"
gunicorn rmxweb.wsgi:application --bind 0.0.0.0:8000
