# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
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

ENVIRONMENT_NAME = 'dev'

TIMEZONE = 'US/Eastern'

REFRESH_CONFIG = {
    'multiplier': 1,
    'min': 1,
    'email_recipient': 'mettel.team@intelygenz.com',
    'stop_delay': 0,
    'refresh_map_minutes': 60 * 4,
    'semaphore': 10,
    'monitorable_management_statuses': {"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"},
    "attempts_threshold": 10,
}

LOG_CONFIG = {
    'name': 'hawkeye-customer-cache',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-t7-bridge'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': 0
    },
}

QUART_CONFIG = {
    'title': 'hawkeye-customer-cache',
    'port': 5000
}

REDIS = {
    "host": "redis"
}

REDIS_CUSTOMER_CACHE = {
    "host": "redis-customer-cache"
}
