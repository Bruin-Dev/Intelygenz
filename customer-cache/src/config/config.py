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
    'multiplier': 1,
    'min': 1,
    'stop_delay': 600,
    'reconnects': 150
}

SCHEDULER_CONFIG = {
    'timezone': 'US/Eastern'
}
ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

VELOCLOUD_HOST = [
    "mettel.velocloud.net",
    "metvco02.mettel.net",
    "metvco03.mettel.net",
    "metvco04.mettel.net",
]

REFRESH_CONFIG = {
    'timezone': 'US/Eastern',
    'email_recipient': 'mettel.alerts@intelygenz.com',
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'refresh_map_minutes': 60 * 4,
    'refresh_check_interval_minutes': 5,
    'blacklisted_edges': [
        # Federal edge that is inside a non-federal Velocloud instance
        {'host': 'mettel.velocloud.net', 'enterprise_id': 170, 'edge_id': 3195}
    ],
    'semaphore': 3,
    'velo_servers': [
        {"mettel.velocloud.net": []},
        {"metvco02.mettel.net": []},
        {"metvco03.mettel.net": []},
        {"metvco04.mettel.net": []},
    ],
    'environment': ENVIRONMENT_NAME,
    'monitorable_management_statuses': {"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"},
    "attempts_threshold": 10,
}

LOG_CONFIG = {
    'name': 'customer-cache',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-t7-bridge'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
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
