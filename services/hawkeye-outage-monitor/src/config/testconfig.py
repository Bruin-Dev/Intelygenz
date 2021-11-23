# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'multiplier': 1,
    'min': 1,
    'stop_delay': 600,
    'reconnects': 150
}

quarantine_time = 5

MONITOR_CONFIG = {
    'multiplier': 1,
    'min': 1,
    'stop_delay': 0,
    'environment': "dev",
    'timezone': "US/Eastern",
    'jobs_intervals': {
        'outage_monitor': 60 * 3,
        'quarantine': quarantine_time,
    },
    'semaphore': 10,
    'autoresolve_ticket_creation_seconds': 60 * 60,
    'autoresolve_last_outage_seconds': 60 * 60,
}

ENVIRONMENT_NAME = "dev"

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'hawkeye-outage-monitor',
    'port': 5000
}

REDIS = {
    "host": 'redis-host'
}

METRICS_SERVER_CONFIG = {
    'port': 9090,
}
