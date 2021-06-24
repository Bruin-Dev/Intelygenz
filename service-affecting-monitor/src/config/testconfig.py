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
    'environment': "test",
    'timezone': 'US/Eastern',
    'monitoring_seconds': 600,
    "latency": 140,
    "packet_loss": 8,
    "jitter": 50,
    "bandwidth_percentage": 90,
    'monitoring_minutes_interval': 10,
    "monitoring_minutes_per_trouble": {
        "latency": 30,
        "packet_loss": 30,
        "jitter": 30,
        "bandwidth": 30,
    },
    'forward_to_hnoc': 60,
    'autoresolve': {
        'semaphore': 3,
        'metrics_lookup_interval_minutes': 30,
        'last_affecting_trouble_seconds': 75 * 60,
        'max_autoresolves': 3,
    },
}

MONITOR_REPORT_CONFIG = {
    "semaphore": 5,
    'wait_fixed': 1,
    'stop_after_attempt': 2,
    'environment': "test",
    'crontab': '0 8 * * *',
    'client_id_bandwidth': 83109,
    'threshold': 3,
    'active_reports': ['Jitter', 'Latency', 'Packet Loss', 'Bandwidth Over Utilization'],
    'trailing_days': 14,
    'monitoring_minutes_interval': 10,
    'timezone': 'US/Eastern',
    "report_config_by_trouble": {
        'bandwidth': {
            'client_ids': [83109],
            'recipient': ['mettel@intelygenz.com']
        },
        'default': {
            'recipient': ['mettel@intelygenz.com']
        },
    }
}

ENVIRONMENT_NAME = "dev"

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
