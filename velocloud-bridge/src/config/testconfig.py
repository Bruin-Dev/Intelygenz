# You must replicate the structure of config.py, changing os.environ calls for mock values
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
    'multiplier': 0.1,
    'min': 0,
    'stop_delay': 0.4,
    'timezone': 'US/Eastern',
    'ids_by_serial_cache_ttl': 86400

}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.INFO,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

GRAFANA_CONFIG = {
    'port': 9090,
    'time': 1
}
