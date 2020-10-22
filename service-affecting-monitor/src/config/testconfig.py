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

MONITOR_CONFIG = {
    'recipient': "some.recipient@email.com",
    'device_by_id': contact_info.devices_by_id,
    'environment': "dev",
    'timezone': 'US/Eastern',
    'monitoring_seconds': 600,
    "latency": 120,
    "packet_loss": 8,
    "jitter": 30,
    'monitoring_minutes_interval': 10,
    "monitoring_minutes_per_trouble": {
        "latency": 10,
        "packet_loss": 10,
        "jitter": 10,
    },
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-affecting-monitor',
    'port': 5000
}
