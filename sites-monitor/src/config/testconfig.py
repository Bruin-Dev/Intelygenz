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

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}

ENVIRONMENT_NAME = 'dev'

SITES_MONITOR_CONFIG = {
    'monitoring_seconds': 0.01,
    'timezone': 'US/Eastern',
    'semaphore': 5,
    'jobs_intervals': {
        'edge_monitor': 0.01,
    },
}

QUART_CONFIG = {
    'title': 'sites-monitor',
    'port': 5000
}
