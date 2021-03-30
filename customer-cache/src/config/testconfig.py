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

SCHEDULER_CONFIG = {
    'timezone': 'US/Eastern'
}
ENVIRONMENT_NAME = 'dev'

VELOCLOUD_HOST = [
        "mettel.velocloud.net",
        "metvco02.mettel.net",
        "metvco03.mettel.net",
        "metvco04.mettel.net",
]

REFRESH_CONFIG = {
    'timezone': 'US/Eastern',
    'email_recipient': 'mettel.team@intelygenz.com',
    'multiplier': 1,
    'min': 1,
    'stop_delay': 0,
    'refresh_map_minutes': 60 * 4,
    'blacklisted_edges': [
        # Simulate a federal edge that is inside a non-federal Velocloud instance
        {'host': 'mettel.velocloud.net', 'enterprise_id': 11888, 'edge_id': 12345}
    ],
    'semaphore': 10,
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
        'port': 0
    },
}

QUART_CONFIG = {
    'title': 'customer-cache',
    'port': 5000
}

REDIS = {
    "host": "redis"
}

REDIS_CUSTOMER_CACHE = {
    "host": "redis-customer-cache"
}
