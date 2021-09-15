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
    'refresh_check_interval_minutes': 5,
    'blacklisted_edges': [
        # Simulate a federal edge that is inside a non-federal Velocloud instance
        {'host': 'mettel.velocloud.net', 'enterprise_id': 11888, 'edge_id': 12345}
    ],
    'blacklisted_client_ids': [83109, 89267, 87671, 88377, 87915, 88854, 87903, 88012, 89242, 89044, 88912, 89180,
                               89317, 88748, 89401, 88792, 87916, 89309, 89544, 89268, 88434, 88873, 89332, 89416,
                               89235, 88550, 89160, 89162, 88345, 88803, 89336, 83763, 89024, 88883, 88848, 89322,
                               89261, 89191, 89190, 88286, 88272, 88509, 88859, 88110, 88926, 89164, 89233, 88417,
                               88270, 88698, 89134, 88839, 87957, 89279, 87978, 89342, 88987, 89441, 88989, 89195,
                               82368, 89353, 89305, 89548, 89080, 88271, 89023, 87955, 88715, 89139, 89077, 89341,
                               88015, 89521, 89665, 88293, 89321, 89501, 89072, 89107, 88187, 89556, 89323, 88416,
                               89326],
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
