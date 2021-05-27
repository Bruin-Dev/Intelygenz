import os
import sys
import logging
from dotenv import load_dotenv

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 't7-bridge',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-t7-bridge'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}


def get_config():
    APP_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')  # refers to application_top
    dotenv_path = os.path.join(APP_ROOT, 'config/.env')
    load_dotenv(dotenv_path)

    mongo_url = f'mongodb://{os.getenv("MONGODB_USERNAME")}:{os.getenv("MONGODB_PASSWORD")}@' \
                f'{os.getenv("MONGODB_HOST")}/{os.getenv("MONGODB_DATABASE")}'

    return {
        'sentry': {
            'config': {
                'release': os.getenv('VERSION')
            },
            'dsn': os.getenv('SENTRY_DSN')
        },
        'mongo': {
            'url': mongo_url
        },
        'bruin': {
            'id': os.getenv('BRUIN_CLIENT_ID'),
            'secret': os.getenv('BRUIN_CLIENT_SECRET')
        },
        'interval_tasks_server': int(os.getenv('INTERVAL_TASKS_RUN')),
    }
