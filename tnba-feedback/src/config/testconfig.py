# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys
import os

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    },
    'multiplier': 0.1,
    'min': 0,
    'stop_delay': 0.1,
    'reconnects': 0
}
MONITORING_INTERVAL_SECONDS = 60 * 60

TNBA_FEEDBACK_CONFIG = {
    'environment': "dev",
    'timezone': "US/Eastern",
    'semaphore': 1,
    'velo_filter': {"mettel.velocloud.net": []},
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'tnba-feedback',
    'port': 5000
}

REDIS = {
    "host": "redis"
}
