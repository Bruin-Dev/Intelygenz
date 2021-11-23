# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

LUMIN_CONFIG = {
    'uri': os.environ["LUMIN_URI"],
    'token': os.environ["LUMIN_TOKEN"],
    'multiplier': 1,
    'min': 4,
    'stop_delay': 10
}

BILLING_REPORT_CONFIG = {
    'customer_name': os.environ["CUSTOMER_NAME"],
    'recipient': os.environ["BILLING_RECIPIENT"],
    'timezone': 'US/Eastern',
    'date_format': '%m/%d/%Y',
    'fieldnames': [
        'id',
        'conversation_id',
        'type',
        'host_id',
        'host_did',
        'user_did',
        'timestamp',
        'fake'
    ]
}

EMAIL_CONFIG = {
    'sender_email': 'mettel.automation@intelygenz.com',
    'password': os.environ["EMAIL_ACC_PWD"]
}

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME', 'local')

LOG_CONFIG = {
    'name': 'lumin-billing-report',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-lumin-billing-report'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'lumin-billing-report',
    'port': 5000
}
