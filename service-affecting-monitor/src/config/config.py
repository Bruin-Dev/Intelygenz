# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys
from config import contact_info

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

MONITOR_CONFIG = {
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'device_by_id': contact_info.devices_by_id,
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    "latency": 120,
    "packet_loss": 8,
    "jitter": 30,
    "bandwidth_percentage": 90,
    'monitoring_minutes_interval': 10,
    "monitoring_minutes_per_trouble": {
        "latency": 20,
        "packet_loss": 20,
        "jitter": 20,
        "bandwidth": 20,
    }
}

MONITOR_REPORT_CONFIG = {
    'semaphore': 5,
    'wait_fixed': 15,
    'stop_after_attempt': 3,
    'reports': [
        {
            'name': 'Report - Bandwitdh Over Utilization',
            'type': 'bandwitdh_over_utilization',
            'crontab': '0 8 * * *',
            'threshold': 3,  # Number of tickets to include in the report
            'client_id': 83109,
            'trailing_days': 14,
            'recipient': 'bsullivan@mettel.net, jtaylor@mettel.net, mettel.automation@intelygenz.com'
        }
    ]
}

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'service-affecting-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-service-affecting-monitor'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'service-affecting-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}
