"""Configuration used by applications."""

import os

from . import celery_settings

# crawl settings
DEFAULT_CRAWL_DEPTH = 2

# Configurations that are related to the corpus and its data storage
# DATA_ROOT is the path to the directory that will store corpora and data
# generated by rmxbot
DATA_ROOT = os.environ.get('DATA_ROOT', '/data')

# the tmp directory used by rmxbot when processing files, etc...
# TMP_DATA_DIR = '/data/tmp'
TMP_DATA_DIR = os.environ.get('TMP_DATA_DIR')

EXTRACTXT_ENDPOINT = os.environ.get('EXTRACTXT_ENDPOINT')

EXTRACTXT_FILES_UPLOAD_URL = '{}/upload-files'.format(EXTRACTXT_ENDPOINT)

# The path to the directory where corpora along with matrices are stored.
CONTAINER_ROOT = os.path.join(DATA_ROOT, 'container')
TEXT_FOLDER = 'text'
MATRIX_FOLDER = 'matrix'

CORPUS_MAX_SIZE = 500

# todo(): create a configuration for the connection to the sql database

# monitor the crawl every 5 seconds
CRAWL_MONITOR_COUNTDOWN = 5
# wait 10 s before starting to monitor
CRAWL_START_MONITOR_COUNTDOWN = 10

REQUEST_MAX_RETRIES = 5
# time to wait in seconds after the last call made inside the crawler.
# after that the container is set as ready
SECONDS_AFTER_LAST_CALL = 30

# =========================================>

# RabbitMQ configuration
# rabbitmq rpc queue name
# todo(): delete these
# RPC_QUEUE_NAME = os.environ.get('RPC_QUEUE_NAME', 'rmxweb')
# RPC_PUBLISH_QUEUES = {
#     'nlp': 'nlp',
#     'scrasync': 'scrasync',
#     'rmxgrep': 'rmxgrep',
#     'extractxt': 'extractxt'
# }
# RabbitMQ login credentials

# =========================================<


# configurations for prometheus
PROMETHEUS_HOST = os.environ.get('PROMETHEUS_HOST')
PROMETHEUS_PORT = os.environ.get('PROMETHEUS_PORT')
PROMETHEUS_URL = f'{PROMETHEUS_HOST}:{PROMETHEUS_PORT}/api/v1'
PROMETHEUS_JOB = 'rmxweb'

PUSHGATEWAY_PORT = os.environ.get('PUSHGATEWAY_PORT')
PUSHGATEWAY_HOST = os.environ.get('PUSHGATEWAY_HOST')


# celery task routes - these are imported in the apps or tasks
RMXWEB_TASKS = celery_settings.RMXWEB_TASKS
RMXGREP_TASK = celery_settings.RMXGREP_TASK
SCRASYNC_TASKS = celery_settings.SCRASYNC_TASKS
NLP_TASKS = celery_settings.NLP_TASKS
RMXCLUSTER_TASKS = celery_settings.RMXCLUSTER_TASKS


# hexdigest size
DIGEST_SIZE = 64
HEXDIGEST_SIZE = 128


# the type of data to return to the client
OUTPUT_TYPE_JSON = os.environ.get('OUTPUT_TYPE_JSON', False)

# available data formats for http responses
AVAILABLE_FORMATS = ['json', 'csv']

