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

ENV_CONFIG = {
    'environment': 'dev',
}

MONITOR_CONFIG = {
    'recipient': "some.recipient@email.com",
    'timezone': 'US/Eastern',
    'monitoring_seconds': 600,
    "latency_wireless": 120,
    "latency_wired": 50,
    "packet_loss_wireless": 8,
    "packet_loss_wired": 5,
    'monitoring_minutes': 10
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
