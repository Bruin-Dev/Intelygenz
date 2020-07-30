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

DISPATCH_MONITOR_CONFIG = {
    'timezone': 'US/Eastern',
    'jobs_intervals': {
        'dispatch_monitor': 60 * 3
    },
}

DISPATCH_PORTAL_CONFIG = {
    'title': 'Dispatch Portal API',
    'port': os.environ['DISPATCH_PORTAL_SERVER_PORT'],
    'schema_path': './src/schema.json',
    'swagger_path': './src/swagger.yml',
    'swagger_url_prefix': '/api/doc',
    'swagger_title': 'Dispatch Portal API doc'
}

CTS_CONFIG = {
    # Email for requests and cancellations
    'email': 'CTS-MettelService@core-techs.com'
}

LIT_CONFIG = {
    # Email for requests and cancellations
    'email': 'dispatch@litnetworking.com'
}

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'dispatch-portal-backend',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    # 'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-dispatch-portal-backend'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
