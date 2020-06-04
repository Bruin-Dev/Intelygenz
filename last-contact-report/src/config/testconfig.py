# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'client_ID': 'last-contact-report-test',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.INFO,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}


ALERTS_CONFIG = {
    'last_contact': {
        'recipient': "some.recipient@email.com",
    },
    'timezone': 'US/Eastern'
}


QUART_CONFIG = {
    'title': 'last-contact-report',
    'port': 5000
}
