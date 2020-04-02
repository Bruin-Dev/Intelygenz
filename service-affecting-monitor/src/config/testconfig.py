# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys
from config import contact_info

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

MONITOR_CONFIG = {
    'recipient': "some.recipient@email.com",
    'device_by_id': contact_info.devices_by_id,
    'environment': "dev",
    'timezone': 'US/Eastern',
    'monitoring_seconds': 600,
    "latency_wireless": 120,
    "latency_wired": 50,
    "packet_loss_wireless": 8,
    "packet_loss_wired": 5,
    "jitter": 30,
    'monitoring_minutes': 10,
    "management_status_filter": {
        "Pending",
        "Active – Gold Monitoring",
        "Active – Platinum Monitoring"
    }
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
