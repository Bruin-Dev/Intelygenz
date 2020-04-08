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

LIT_CONFIG = {
    'client_id': os.environ["LIT_CLIENT_ID"],
    'client_secret': os.environ["LIT_CLIENT_SECRET"],
    'client_username': os.environ["LIT_CLIENT_USERNAME"],
    'client_password': os.environ["LIT_CLIENT_PASSWORD"],
    'client_security_token': os.environ["LIT_CLIENT_SECURITY_TOKEN"],
    'login_url': os.environ["LIT_LOGIN_URL"],
    'domain': os.environ["LIT_DOMAIN"],
    'attempts': 5,
    'wait_fixed': 3,
    'multiplier': 5,
    'min': 5,
    'stop_delay': 18000,
    'timezone': 'US/Eastern',
    'login_ttl': 90
}

LOG_CONFIG = {
    'name': 'lit-bridge',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'lit-bridge',
    'port': 5000
}

GRAFANA_CONFIG = {
    'port': 9090,
    'time': 1500
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
