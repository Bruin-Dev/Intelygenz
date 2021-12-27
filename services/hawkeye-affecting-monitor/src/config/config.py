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
    'reconnects': 150,
}

TIMEZONE = os.environ['TIMEZONE']

MONITOR_CONFIG = {
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'scan_interval': int(os.environ['PROBES_TESTS_RESULTS_LOOKUP_INTERVAL']) // 60,
    'jobs_intervals': {
        'affecting_monitor': int(os.environ['MONITORING_JOB_INTERVAL']) // 60,
    },
    'semaphores': {
        'bruin': 5,
    },
    'product_category': os.environ['MONITORED_PRODUCT_CATEGORY'],
}

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

LOG_CONFIG = {
    'name': 'hawkeye-affecting-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.environ['PAPERTRAIL_ACTIVE'] == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-hawkeye-affecting-monitor'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'hawkeye-affecting-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090,
}
