# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

from aiohttp import TraceConfig


def generate_aio_tracers(**kwargs):
    usage_repository = kwargs['endpoints_usage_repository']

    async def bruin_usage_on_request_cb(session, trace_config_ctx, params):
        usage_repository.increment_usage(params.method, params.url.path)

    bruin_api_usage = TraceConfig()
    bruin_api_usage.on_request_start.append(bruin_usage_on_request_cb)

    AIOHTTP_CONFIG['tracers'] = [
        bruin_api_usage,
    ]


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

BRUIN_CONFIG = {
    'base_url': os.environ["BRUIN_BASE_URL"],
    'client_id': os.environ["BRUIN_CLIENT_ID"],
    'client_secret': os.environ["BRUIN_CLIENT_SECRET"],
    'login_url': os.environ["BRUIN_LOGIN_URL"],
}

ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

LOG_CONFIG = {
    'name': 'bruin-bridge',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.environ['PAPERTRAIL_ACTIVE'] == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-bruin-bridge'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

AIOHTTP_CONFIG = {
    'tracers': []
}

QUART_CONFIG = {
    'title': 'bruin-bridge',
    'port': 5000
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
