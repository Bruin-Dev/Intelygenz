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

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

TIMEZONE = os.environ['TIMEZONE']

DIGI_CONFIG = {
    'days_of_digi_recovery_log': int(os.environ["LOGS_LOOKUP_INTERVAL"]) // 60 // 60 // 24,
    'digi_reboot_report_time': int(os.environ["JOB_INTERVAL"]) // 60,
    'recipient': os.environ["RECIPIENT"],
}


LOG_CONFIG = {
    'name': 'digi-reboot-report',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-last-contact-report'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'digi-reboot-report',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}
