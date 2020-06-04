# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

SLACK_CONFIG = {
    'webhook': ['https://test-slack.com'],
    'time': 1
}

EMAIL_CONFIG = {
    'sender_email': 'fake@gmail.com',
    'password': '456',
    'recipient_email': 'fake@gmail.com'
}

TELESTAX_CONFIG = {
    'url': 'https://fake-telestax.com',
    'account_sid': 'ACCOUNT_SID',
    'auth_token': 'AUTH_TOKEN',
    'from': '16666666666',
    'wait_fixed': 3,
    'stop_after_attempt': 2,
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.INFO,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}
