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

CURRENT_ENVIRONMENT = os.environ['CURRENT_ENVIRONMENT']
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

TIMEZONE = os.environ['TIMEZONE']

FRAUD_CONFIG = {
    'monitoring_interval': int(os.environ['MONITORING_JOB_INTERVAL']) // 60,
    'inbox_email': os.environ['OBSERVED_INBOX_EMAIL_ADDRESS'],
    'sender_emails_list': json.loads(os.environ['OBSERVED_INBOX_SENDERS']),
    'default_contact': json.loads(os.environ['DEFAULT_CONTACT_FOR_NEW_TICKETS']),
    'default_client_info': json.loads(os.environ['DEFAULT_CLIENT_INFO_FOR_DID_WITHOUT_INVENTORY']),
}

LOG_CONFIG = {
    'name': 'fraud-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-fraud-monitor'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'fraud-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
