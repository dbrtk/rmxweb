#!/bin/sh

set -e

gunicorn rmxweb.wsgi:application --bind 0.0.0.0:8000
