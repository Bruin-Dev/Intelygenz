# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys
import os

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'intermapper-outage-monitor',
    'port': 5000
}

ENVIRONMENT_NAME = "dev"

INTERMAPPER_CONFIG = {
    'environment': ENVIRONMENT_NAME,
    'timezone': 'US/Eastern',
    'monitoring_interval': 60 * 10,
    'inbox_email': 'fake@gmail.com',
    'sender_emails_list': ['fakesender@email.com'],
    'intermapper_events': ['Down', 'Critical', 'Alarm', 'Warning']

}
