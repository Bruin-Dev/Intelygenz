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

TIMEZONE = os.environ["TIMEZONE"]

MONITOR_CONFIG = {
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'jobs_intervals': {
        'outage_monitor': int(os.environ["MONITORING_JOB_INTERVAL"]),
        'quarantine': int(os.environ["QUARANTINE_FOR_DEVICES_IN_OUTAGE"]),
    },
    'semaphore': 10,
    'autoresolve_last_outage_seconds': int(os.environ["GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE"]),
}

CURRENT_ENVIRONMENT = os.environ['CURRENT_ENVIRONMENT']
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

LOG_CONFIG = {
    'name': 'hawkeye-outage-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-hawkeye-outage-monitor'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'hawkeye-outage-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090,
}
