import os
import sys
import logging
from dotenv import load_dotenv

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'ticket-statistics',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-ticket-statistics'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}


def get_config():
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')  # refers to application_top
    dotenv_path = os.path.join(APP_ROOT, 'config/.env')
    load_dotenv(dotenv_path)

    mongo_url = f'mongodb://{os.getenv("MONGODB_USERNAME")}:{os.getenv("MONGODB_PASSWORD")}@' \
                f'{os.getenv("MONGODB_HOST")}/{os.getenv("MONGODB_DATABASE")}' \
                f'?ssl=true&ssl_ca_certs=/service/app/rds-combined-ca-bundle.pem&replicaSet=rs0' \
                f'&readPreference=secondaryPreferred&retryWrites=false'
    return {
        'mongo': {
            'url': mongo_url,
        },
        'server': {
            'port': os.getenv('SERVER_PORT', 8000),
            'root_path': os.getenv('SERVER_ROOT_PATH', '/api'),
            'version': os.getenv('SERVER_VERSION', '1.0.0'),
            'name': os.getenv('SERVER_NAME', 'ticket-statistics')
        }
    }
