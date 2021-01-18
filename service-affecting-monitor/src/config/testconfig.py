# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys
from config import contact_info

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

MONITOR_CONFIG = {
    'recipient': "some.recipient@email.com",
    'device_by_id': contact_info.devices_by_id,
    'environment': "dev",
    'timezone': 'US/Eastern',
    'monitoring_seconds': 600,
    "latency": 120,
    "packet_loss": 8,
    "jitter": 30,
    "bandwidth_percentage": 80,
    'monitoring_minutes_interval': 10,
    "monitoring_minutes_per_trouble": {
        "latency": 10,
        "packet_loss": 10,
        "jitter": 10,
        "bandwidth": 15,
    },
}

MONITOR_REPORT_CONFIG = {
    "semaphore": 5,
    'wait_fixed': 1,
    'stop_after_attempt': 2,
    'reports': [
        {
            'name': 'Report - Bandwitdh Over Utilization',
            'type': 'bandwitdh_over_utilization',
            'crontab': '20 16 * * *',
            'threshold': 3,  # Number of tickets to include in the report
            'client_id': 83109,
            'trailing_days': 14,
            'recipient': 'mettel@intelygenz.com'
        }
    ]
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-affecting-monitor',
    'port': 5000
}
