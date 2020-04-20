# You must replicate the structure of config.py, changing os.environ calls for mock values
import os
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'client_ID': 'dispatch-portal-backend',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

DISPATCH_PORTAL_CONFIG = {
    'title': 'Dispatch Portal API',
    'port': 5000,
    'schema_path': './src/schema.json',
    'swagger_path': './src/swagger.yml',
    'swagger_url_prefix': '/api/doc',
    'swagger_title': 'Dispatch Portal API doc'
}

LOG_CONFIG = {
    'name': 'dispatch-portal-backend-test',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'Dispatch Portal API',
    'port': 5000
}
