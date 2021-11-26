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

VELOCLOUD_CONFIG = {
    'verify_ssl': False,
    'servers': [
        {
            'url': 'someurl',
            'username': 'someusername',
            'password': 'somepassword',

        }
    ],
    'timezone': 'US/Eastern',
    'ids_by_serial_cache_ttl': 86400

}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}