import os
import sys
import logging
from dotenv import load_dotenv

ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']
CURRENT_ENVIRONMENT = os.environ['CURRENT_ENVIRONMENT']

LOG_CONFIG = {
    'name': 'ticket-statistics',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == 'true',
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-ticket-statistics'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}


def get_config():
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')  # refers to application_top
    dotenv_path = os.path.join(APP_ROOT, 'config/.env')
    load_dotenv(dotenv_path)

    mongo_user = os.environ["MONGODB_USERNAME"]
    mongo_password = os.environ["MONGODB_PASSWORD"]
    mongo_host = os.environ["MONGODB_HOST"]
    mongo_db = os.environ["MONGODB_DATABASE"]
    mongo_params = get_mongo_params()
    mongo_url = f'mongodb://{mongo_user}:{mongo_password}@{mongo_host}/{mongo_db}?{mongo_params}'

    return {
        'environment_name': ENVIRONMENT_NAME,
        'current_environment': CURRENT_ENVIRONMENT,
        'mongo': {
            'url': mongo_url,
        },
        'server': {
            'port': os.getenv('SERVER_PORT', 8000),
            'root_path': os.getenv('SERVER_ROOT_PATH', '/api'),
            'version': os.getenv('SERVER_VERSION', '1.0.0'),
            'name': os.getenv('SERVER_NAME', 'ticket-statistics'),
        },
        'redis': {
            'host': os.environ['REDIS_HOSTNAME'],
            'ttl': 1 * 60 * 60,
        },
        'human_average_daily_tasks': 34,
    }


def get_mongo_params():
    if ENVIRONMENT_NAME.endswith('local'):
        return 'authSource=admin'
    else:
        return 'ssl=true&ssl_ca_certs=/service/app/rds-combined-ca-bundle.pem' \
               '&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
