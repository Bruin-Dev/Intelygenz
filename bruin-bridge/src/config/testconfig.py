# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-streaming:4222',
    'cluster_name': 'automation-engine-nats',
    'client_ID': 'base-microservice',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

BRUIN_CONFIG = {
    'base_url': "some.bruin.url",
    'client_id': "client_id",
    'client_secret': "client_secret",
    'login_url': "some.login.url"
}

LOG_CONFIG = {
    'name': 'bruin-bridge-test',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

GRAFANA_CONFIG = {
    'port': 9090,
    'time': 1
}
