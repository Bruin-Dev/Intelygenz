# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

MONITOR_CONFIG = {
    'timezone': 'US/Eastern',
    'scheduler_config': {
        'new_created_tickets_feedback': 1,
    },
    'nats_request_timeout': {
        'kre_seconds': 10,
        'bruin_request_seconds': 30
    },
    'semaphores': {
        'created_tickets_concurrent': 10,
    },
}

ENVIRONMENT = 'dev'

ENVIRONMENT_NAME = 'dev'

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}