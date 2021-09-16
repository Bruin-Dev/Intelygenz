# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import os
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
        'repair_ticket_seconds': 1,
        'repair_ticket_feedback_seconds': 10
    },
    'nats_request_timeout': {
        'kre_seconds': 10,
        'post_ticket_seconds': 30
    },
    'semaphores': {
        'repair_ticket_concurrent': 1
    }
}

ENVIRONMENT = 'dev'

ENVIRONMENT_NAME = 'dev'

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}
