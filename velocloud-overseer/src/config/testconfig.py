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

VELOCLOUD_CONFIG = {
    'verify_ssl': 'no',
    'servers': [
        {
            'url': 'someurl',
            'username': 'someusername',
            'password': 'somepassword',

        }
    ],
    'multiplier': 5,
    'min': 5,
    'max': 300,
    'total': 8,
    'backoff_factor': 2

}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

GRAFANA_CONFIG = {
    'port': 9090
}
