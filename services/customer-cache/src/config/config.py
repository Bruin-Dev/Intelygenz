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

TIMEZONE = os.environ['TIMEZONE']

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

VELOCLOUD_HOST = json.loads(os.environ['VELOCLOUD_HOSTS'])

REFRESH_CONFIG = {
    'email_recipient': os.environ['DUPLICATE_INVENTORIES_RECIPIENT'],
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'refresh_map_minutes': int(os.environ['REFRESH_JOB_INTERVAL']) // 60,
    'refresh_check_interval_minutes': int(os.environ['REFRESH_CHECK_INTERVAL']) // 60,
    'blacklisted_edges': json.loads(os.environ['BLACKLISTED_EDGES']),
    'blacklisted_client_ids': json.loads(os.environ['BLACKLISTED_CLIENTS_WITH_PENDING_STATUS']),
    'semaphore': 3,
    'velo_servers': [
        {host: []}
        for host in json.loads(os.environ['VELOCLOUD_HOSTS'])
    ],
    'monitorable_management_statuses': json.loads(os.environ['WHITELISTED_MANAGEMENT_STATUSES']),
    "attempts_threshold": 10,
}

LOG_CONFIG = {
    'name': 'customer-cache',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.environ['PAPERTRAIL_ACTIVE'] == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-customer-cache'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'customer-cache',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

REDIS_CUSTOMER_CACHE = {
    "host": os.environ["REDIS_CUSTOMER_CACHE_HOSTNAME"]
}
