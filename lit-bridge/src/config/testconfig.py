# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'client_ID': 'base-microservice',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    },
    'multiplier': 0.1,
    'min': 0,
    'stop_delay': 0.4,
    'reconnects': 0
}

LIT_CONFIG = {
    'client_id': '__LIT_CLIENT_ID__',
    'client_secret': "__LIT_CLIENT_SECRET__",
    'client_username': "__LIT_CLIENT_USERNAME__",
    'client_password': "__LIT_CLIENT_PASSWORD__",
    'client_security_token': "__LIT_CLIENT_SECURITY_TOKEN__",
    'login_url': "__LIT_LOGIN_URL__",
    'domain': "test",
    'attempts': 2,
    'wait_fixed': 0.3,
    'multiplier': 0.1,
    'min': 0,
    'stop_delay': 0.4,
    'timezone': 'US/Eastern',
    'login_ttl': 90
}

LOG_CONFIG = {
    'name': 'lit-bridge-test',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}
