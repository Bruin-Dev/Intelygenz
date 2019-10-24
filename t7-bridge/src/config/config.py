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

LOG_CONFIG = {
    'name': 't7-bridge',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

T7CONFIG = {
    'base_url': os.environ['T7_BASE_URL'],
    'client_name': 'mettel-automation',
    'version': '1.0.0',
    'auth-token': os.environ['T7_TOKEN']
}

QUART_CONFIG = {
    'title': 't7-bridge',
    'port': 5000
}
