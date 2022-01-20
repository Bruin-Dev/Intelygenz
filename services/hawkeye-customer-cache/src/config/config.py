# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import json
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'subscriber': {
        'pending_limits': 65536
    },
    'multiplier': 1,
    'min': 1,
    'stop_delay': 600,
    'reconnects': 150
}

ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

TIMEZONE = os.environ['TIMEZONE']

REFRESH_CONFIG = {
    'multiplier': 5,
    'min': 5,
    'email_recipient': 'mettel.alerts@intelygenz.com',
    'stop_delay': 300,
    'refresh_map_minutes': int(os.environ['REFRESH_JOB_INTERVAL']) // 60,
    'semaphore': 1,
    'monitorable_management_statuses': json.loads(os.environ['WHITELISTED_MANAGEMENT_STATUSES']),
    "attempts_threshold": 10,
}

LOG_CONFIG = {
    'name': 'hawkeye-customer-cache',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-t7-bridge'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'hawkeye-customer-cache',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

REDIS_CUSTOMER_CACHE = {
    "host": os.environ["REDIS_CUSTOMER_CACHE_HOSTNAME"]
}
