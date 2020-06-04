# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'subscriber': {
        'max_inflight': 1,
        'pending_limits': 1
    },
    'publisher': {
        'max_pub_acks_inflight': 1
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

CTS_CONFIG = {
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'client_id': os.environ["CTS_CLIENT_ID"],
    'client_secret': os.environ["CTS_CLIENT_SECRET"],
    'client_username': os.environ["CTS_CLIENT_USERNAME"],
    'client_password': os.environ["CTS_CLIENT_PASSWORD"],
    'client_security_token': os.environ["CTS_CLIENT_SECURITY_TOKEN"],
    'login_url': os.environ["CTS_LOGIN_URL"],
    'domain': os.environ["CTS_DOMAIN"],
    'attempts': 5,
    'wait_fixed': 3,
    'multiplier': 5,
    'min': 5,
    'stop_delay': 18000,
    'timezone': 'US/Eastern',
    'login_ttl': 90
}

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'cts-bridge',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-cts-bridge'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'cts-bridge',
    'port': 5000
}

GRAFANA_CONFIG = {
    'port': 9090,
    'time': 1500
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
