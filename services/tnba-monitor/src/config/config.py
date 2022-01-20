# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import json
import logging
import os
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

PRODUCT_CATEGORY = os.environ['MONITORED_PRODUCT_CATEGORY']

MONITOR_CONFIG = {
    'monitoring_interval_seconds': int(os.environ['MONITORING_JOB_INTERVAL']),
    'blacklisted_edges': json.loads(os.environ['BLACKLISTED_EDGES']),
    'semaphore': 1,
    'velo_filter': {
        host: []
        for host in json.loads(os.environ['MONITORED_VELOCLOUD_HOSTS'])
    },
    'tnba_notes_age_for_new_appends_in_minutes': int(os.environ['GRACE_PERIOD_BEFORE_APPENDING_NEW_TNBA_NOTES']) // 60,
    'last_outage_seconds': int(os.environ['GRACE_PERIOD_BEFORE_MONITORING_TICKETS_BASED_ON_LAST_DOCUMENTED_OUTAGE']),
    'request_repair_completed_confidence_threshold': int(
        os.environ['MIN_REQUIRED_CONFIDENCE_FOR_REQUEST_AND_REPAIR_COMPLETED_PREDICTIONS']) / 100,
}


TIMEZONE = os.environ['TIMEZONE']

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

LOG_CONFIG = {
    'name': 'tnba-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-tnba-monitor'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'tnba-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
