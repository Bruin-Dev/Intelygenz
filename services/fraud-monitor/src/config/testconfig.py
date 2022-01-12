# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

ENVIRONMENT_NAME = "dev"

FRAUD_CONFIG = {
    'environment': ENVIRONMENT_NAME,
    'timezone': 'US/Eastern',
    'monitoring_interval': 5,
    'inbox_email': 'mettel.automation@intelygenz.com',
    'sender_emails_list': ['amate@mettel.net'],
    'default_contact': {
        'name': 'Holmdel NOC',
        'email': 'holmdelnoc@mettel.net',
    },
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'fraud-monitor',
    'port': 5000
}
