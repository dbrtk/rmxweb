
import os
import re

# RabbitMQ login credentials
RPC_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS')
RPC_USER = os.environ.get('RABBITMQ_DEFAULT_USER')
RPC_VHOST = os.environ.get('RABBITMQ_DEFAULT_VHOST')

# the host to which the rpc broker (rabbitmq) is deployed
RPC_HOST = os.environ.get('RABBITMQ_HOST')
RPC_PORT = os.environ.get('RABBITMQ_PORT', 5672)

RPC_QUEUE_NAME = os.environ.get('RPC_QUEUE_NAME', 'rmxweb')

# REDIS CONFIG
# celery, redis (auth access) configuration. Reids is being used as a result
# backend.
BROKER_HOST_NAME = os.environ.get('BROKER_HOST_NAME')
REDIS_PASS = os.environ.get('REDIS_PASS')
REDIS_DB_NUMBER = os.environ.get('REDIS_DB_NUMBER')
REDIS_PORT = os.environ.get('REDIS_PORT')


# broker_url = 'amqp://myuser:mypassword@localhost:5672/myvhost'
_url = f'amqp://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}/{RPC_VHOST}'

broker_url = _url

# redis result backend
result_backend = f'redis://:{REDIS_PASS}@{BROKER_HOST_NAME}:{REDIS_PORT}/{REDIS_DB_NUMBER}'

result_persistent = True

imports = ('container.tasks', 'data.tasks', 'graph.receive')

result_expires = 30
timezone = 'UTC'

accept_content = ['json', 'msgpack', 'yaml']
task_serializer = 'json'
result_serializer = 'json'

task_routes = {

    re.compile(r'(data|container|graph)\..*'): {'queue': 'rmxweb'},

    'scrasync.*': {'queue': 'scrasync'},

    'nlp.*': {'queue': 'nlp'},

    'rmxgrep.*': {'queue': 'rmxgrep'},

    'rmxcluster.*': {'queue': 'rmxcluster'},

}

RMXWEB_TASKS = {

    'delete_many': 'data.tasks.delete_many',

    'create_from_webpage': 'data.tasks.create_from_webpage',

    'test_task': 'rmxweb.container.tasks.test_task',

    'delete_data_from_container':
        'container.tasks.delete_data_from_container',

    'process_crawl_resp': 'container.tasks.process_crawl_resp',

    # todo(): review and delete...
    'monitor_crawl': 'container.tasks.monitor_crawl',

    'crawl_metrics': 'container.tasks.crawl_metrics',

    'integrity_check': 'container.tasks.integrity_check',

}

SCRASYNC_TASKS = {

    'launch_crawl': 'scrasync.scraper.launch_crawl',

    'delete_crawl_status': 'scrasync.tasks.delete_many',

}

NLP_TASKS = {

    'compute_matrices': 'nlp.task.compute_matrices',

    'factorize_matrices': 'nlp.task.factorize_matrices',

    'integrity_check': 'nlp.task.integrity_check',

    'available_features': 'nlp.task.available_features',

    'features_and_docs': 'nlp.task.get_features_and_docs',

    'kmeans_cluster': 'nlp.task.kmeans_cluster',

    'kmeans_files': 'nlp.task.kmeans_files',

    'retrieve_features': 'nlp.task.retrieve_features',

    'hierarchical_tree': 'nlp.task.hierarchical_tree',
}

RMXGREP_TASK = {

    'search_text': 'rmxgrep.task.search_text'
}

RMXCLUSTER_TASKS = {

    'kmeans_groups': 'rmxcluster.task.kmeans_groups'
}
