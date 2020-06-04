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


def parse_velocloud_config():
    credential_blocks = os.environ["VELOCLOUD_CREDENTIALS"].split(";")
    credential_blocks_splitted = [credential_block.split("+") for credential_block in credential_blocks]
    return [
        {'url': cred_block[0],
         'username': cred_block[1],
         'password': cred_block[2]
         }
        for cred_block in credential_blocks_splitted]


VELOCLOUD_CONFIG = {
    'verify_ssl': True,
    'servers': parse_velocloud_config(),
    'multiplier': 5,
    'min': 5,
    'stop_delay': 18000,
    'timezone': 'US/Eastern',
    'ids_by_serial_cache_ttl': 86400
}

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'velocloud-bridge',
    'level': logging.INFO,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-velocloud-bridge'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'velocloud-bridge',
    'port': 5000
}

GRAFANA_CONFIG = {
    'port': 9090,
    'time': 1500
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
