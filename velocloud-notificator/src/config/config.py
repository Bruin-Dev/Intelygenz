# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'cluster_name': os.environ["NATS_CLUSTER_NAME"],
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

SLACK_CONFIG = {
    'webhook': [os.environ["SLACK_URL"]],
    'time': 600
}

EMAIL_CONFIG = {
    'sender_email': 'mettel.automation@intelygenz.com',
    'password': os.environ["EMAIL_ACC_PWD"],
    'recipient_email': 'mettel@intelygenz.com'
}


LOG_CONFIG = {
    'name': 'velocloud-notificator',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'velocloud-notificator',
    'port': 5000
}
