# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import os
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

MONITOR_CONFIG = {
    'timezone': 'US/Eastern',
    'prefixes': {
        'ticket_prefix': "ticket_*",
        'email_prefix': "email_*"
    },
    'scheduler_config': {
        'new_emails_seconds': 1,
        'new_tickets_seconds': 1
    },
    'nats_request_timeout': {
        'kre_seconds': 10,
        'post_email_tag_seconds': 30
    },
    'semaphores': {
        'new_emails_concurrent': 1,
        'new_tickets_concurrent': 1,
    },
    'api_server': {
        'title': 'Email Tagger Webhooks API',
        'port': 5000,
        'schema_path': './src/schema.json',
        'swagger_path': './src/swagger.yml',
        'swagger_url_prefix': '/api/doc',
        'swagger_title': 'Email Tagger API Docs',
        'request_signature_secret_key': 'secret',
        'use_request_api_key_header': False,  # Set to False until Bruin can send api-key header
        'request_api_key': '123456',
        'endpoint_prefix': ''
    }
}

ENVIRONMENT = 'dev'

ENVIRONMENT_NAME = 'dev'

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'Email Tagger Webhooks API',
    'port': 5000
}
