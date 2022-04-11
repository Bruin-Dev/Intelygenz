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
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

SLACK_CONFIG = {
    'webhook': os.environ["SLACK_WEBHOOK"],
}

EMAIL_DELIVERY_CONFIG = {
    'email': os.environ['EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_USERNAME'],
    'password': os.environ["EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_PASSWORD"],
}

MONITORABLE_EMAIL_ACCOUNTS = json.loads(os.environ['MONITORABLE_EMAIL_ACCOUNTS'])

ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

LOG_CONFIG = {
    'name': 'notifier',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-notifier'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'notifier',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}
