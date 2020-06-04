# You must replicate the structure of config.py, changing os.environ calls for mock values
import os
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    },
    'multiplier': 0.1,
    'min': 0,
    'stop_delay': 0.4,
    'reconnects': 0
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.INFO,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}


T7CONFIG = {
    'base_url': 'http://test-url.com',
    'client_name': 'test-name',
    'version': '1.0.0',
    'auth-token': 'test-token'
}
