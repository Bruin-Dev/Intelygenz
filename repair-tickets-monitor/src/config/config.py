# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
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
        'repair_ticket_seconds': 10
    },
    'nats_request_timeout': {
        'kre_seconds': 10,
        'post_ticket_seconds': 30
    },
    'semaphores': {
        'repair_ticket_concurrent': 10
    }
}

ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'repair-ticket-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-repair-ticket-monitor'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

REDIS_CACHE = {
    "host": os.environ["REDIS_CACHE_HOSTNAME"]
}
