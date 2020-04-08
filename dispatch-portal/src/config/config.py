# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'subscriber': {
        'max_inflight': 1,
        'pending_limits': 1
    },
    'publisher': {
        'max_pub_acks_inflight': 1
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150

}

DISPATCH_PORTAL_CONFIG = {
    'title': 'Dispatch Portal API',
    'port': os.environ['DISPATCH_PORTAL_SERVER_PORT'],
    'schema_path': './schema.json',
    'swagger_path': './swagger.yml',
    'swagger_url_prefix': '/api/doc',
    'swagger_title': 'Dispatch Portal API doc'
}

LOG_CONFIG = {
    'name': 'dispatch-portal',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'dispatch-portal',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
