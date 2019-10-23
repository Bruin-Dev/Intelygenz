# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'cluster_name': os.environ["NATS_CLUSTER_NAME"],
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

BRUIN_CONFIG = {
    'base_url': os.environ["BRUIN_BASE_URL"],
    'client_id': os.environ["BRUIN_CLIENT_ID"],
    'client_secret': os.environ["BRUIN_CLIENT_SECRET"],
    'login_url': os.environ["BRUIN_LOGIN_URL"],
    'multiplier': 5,
    'min': 5,
    'stop_delay': 18000
}

LOG_CONFIG = {
    'name': 'bruin-bridge',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'bruin-bridge',
    'port': 5000
}

GRAFANA_CONFIG = {
    'port': 9090,
    'time': 1500
}
