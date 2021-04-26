
import os

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

imports = ('container.tasks', 'data.tasks')

result_expires = 30
timezone = 'UTC'

accept_content = ['json', 'msgpack', 'yaml']
task_serializer = 'json'
result_serializer = 'json'

task_routes = {

    # 'rmxweb.*': {'queue': 'rmxweb'},
    # 'container.*': {'queue': 'rmxweb'},
    # 'data.*': {'queue': 'rmxweb'},

    'scrasync.*': {'queue': 'scrasync'},

    'nlp.*': {'queue': 'nlp'},

    'rmxgrep.*': {'queue': 'rmxgrep'},

    'rmxcluster.*': {'queue': 'rmxcluster'},

}

RMXWEB_TASKS = {

    'delete_data': 'data.tasks.delete_data',

    'create_from_webpage': 'data.tasks.create_from_webpage',

    'create': 'data.tasks.create',


    'test_task': 'container.tasks.test_task',

    'generate_matrices_remote':
        'container.tasks.generate_matrices_remote',

    'crawl_async': 'container.tasks.crawl_async',

    'nlp_callback_success': 'container.tasks.nlp_callback_success',

    'file_extract_callback': 'container.tasks.file_extract_callback',

    'integrity_check': 'container.tasks.integrity_check',

    'integrity_check_callback':
        'container.tasks.integrity_check_callback',

    'delete_data_from_container':
        'container.tasks.delete_data_from_container',

    'expected_files': 'container.tasks.expected_files',

    'create_from_upload': 'container.tasks.create_from_upload',

    'process_crawl_resp': 'container.tasks.process_crawl_resp',

    'monitor_crawl': 'container.tasks.monitor_crawl',

    'crawl_metrics': 'container.tasks.crawl_metrics',

}

SCRASYNC_TASKS = {

    'create':  'scrasync.scraper.start_crawl',

}

NLP_TASKS = {

    'compute_matrices': 'nlp.task.compute_matrices',

    'factorize_matrices': 'nlp.task.factorize_matrices',

    'integrity_check': 'nlp.task.integrity_check',

    'available_features': 'nlp.task.available_features',

    'features_and_docs': 'nlp.task.get_features_and_docs',

    'kmeans_cluster': 'nlp.task.kmeans_cluster',

    'kmeans_files': 'nlp.task.kmeans_files',

}

RMXGREP_TASK = {

    'search_text': 'rmxgrep.task.search_text'
}

RMXCLUSTER_TASKS = {

    'kmeans_groups': 'rmxcluster.task.kmeans_groups'
}
