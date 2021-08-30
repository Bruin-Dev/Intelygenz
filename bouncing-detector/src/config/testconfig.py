# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys
from config import contact_info

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

ENVIRONMENT_NAME = "dev"

BOUNCING_DETECTOR_CONFIG = {
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'monitoring_minutes_interval': 30,
    'past_events_minutes': 60,
    'event_threshold': 10,
    'device_by_id': contact_info.devices_by_id,
    'environment': ENVIRONMENT_NAME,
    'timezone': 'US/Eastern',
    'velocloud_host': 'mettel.velocloud.net',
}


LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'bouncing-detector',
    'port': 5000
}
