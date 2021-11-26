# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'client_ID': 'base-microservice',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    },
    'multiplier': 0.1,
    'min': 0,
    'stop_delay': 0.4,
    'reconnects': 0
}

BRUIN_CONFIG = {
    'base_url': "some.bruin.url",
    'client_id': "client_id",
    'client_secret': "client_secret",
    'login_url': "some.login.url",
}

LOG_CONFIG = {
    'name': 'bruin-bridge-test',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}