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
    'max_retries_error_404': 5,
    'tag_ids': {
        "Repair": 1,
        "New Order": 2,
        "Change": 3,
        "Billing": 4,
        "Other": 5
    },
    'scheduler_config': {
        'repair_ticket_monitor': 10,
        'new_created_tickets_feedback': 1,
    },
    'nats_request_timeout': {
        'kre_seconds': 10,
        'bruin_request_seconds': 30
    },
    'semaphores': {
        'repair_tickets_concurrent': 10,
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
