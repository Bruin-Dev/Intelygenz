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

SLACK_CONFIG = {
    'webhook': [os.environ["SLACK_URL"]],
    'time': 600
}

EMAIL_CONFIG = {
    'sender_email': 'mettel.automation@intelygenz.com',
    'password': os.environ["EMAIL_ACC_PWD"]
}
EMAIL_ACCOUNTS = {
    'mettel.automation@intelygenz.com': os.environ["EMAIL_ACC_PWD"],
}

TELESTAX_CONFIG = {
    'url': os.environ['TELESTAX_URL'],
    'account_sid': os.environ["TELESTAX_ACCOUNT_SID"],
    'auth_token': os.environ["TELESTAX_AUTH_TOKEN"],
    'from': os.environ["TELESTAX_FROM_PHONE_NUMBER"],
    'wait_fixed': 15,
    'stop_after_attempt': 2,
}
ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'notifier',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-notifier'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'notifier',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
