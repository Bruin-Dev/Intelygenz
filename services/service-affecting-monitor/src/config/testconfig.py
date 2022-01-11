# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

from application import AffectingTroubles

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

TIMEZONE = 'US/Eastern'

PRODUCT_CATEGORY = 'SD-WAN'

MONITOR_CONFIG = {
    'recipient': 'some.recipient@email.com',
    'contact_by_host_and_client_id': {
        'test-host': {
            1234: [
                {
                    "email": 'test@test.com',
                    "name": 'Test',
                    "type": "ticket",
                },
                {
                    "email": 'test@test.com',
                    "name": 'Test',
                    "type": "site",
                },
            ],
        },
    },
    'velo_filter': {
        'test-host': [],
    },
    'environment': 'test',
    'monitoring_minutes_interval': 10,
    'thresholds': {
        AffectingTroubles.LATENCY: 140,                    # milliseconds
        AffectingTroubles.PACKET_LOSS: 8,                  # packets
        AffectingTroubles.JITTER: 50,                      # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 90,  # percentage of total bandwidth
        AffectingTroubles.BOUNCING: 10,                    # number of down / dead events
    },
    'monitoring_minutes_per_trouble': {
        AffectingTroubles.LATENCY: 30,
        AffectingTroubles.PACKET_LOSS: 30,
        AffectingTroubles.JITTER: 30,
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 30,
        AffectingTroubles.BOUNCING: 60,
    },
    'forward_to_hnoc': 60,
    'autoresolve': {
        'semaphore': 3,
        'metrics_lookup_interval_minutes': 30,
        'last_affecting_trouble_seconds': 75 * 60,
        'max_autoresolves': 3,
        'thresholds': {
            AffectingTroubles.BOUNCING: 4,
        },
    },
    'customers_with_bandwidth_enabled': [1, 2, 3],
}

MONITOR_REPORT_CONFIG = {
    'exec_on_start': False,
    'environment': 'test',
    'semaphore': 5,
    'wait_fixed': 1,
    'stop_after_attempt': 2,
    'crontab': '0 8 * * *',
    'threshold': 3,
    'active_reports': ['Jitter', 'Latency', 'Packet Loss', 'Bandwidth Over Utilization'],
    'trailing_days': 14,
    'recipients': {
        'default': ['mettel.automation@intelygenz.com'],
        9994: ['HNOCleaderteam@mettel.net'],
    }
}

BANDWIDTH_REPORT_CONFIG = {
    'exec_on_start': False,
    'environment': 'test',
    'timezone': 'US/Eastern',
    'crontab': '0 8 * * *',
    'lookup_interval_hours': 24,
    'clients': [9994],
    'recipients': ['mettel.automation@intelygenz.com']
}

CURRENT_ENVIRONMENT = 'dev'
ENVIRONMENT_NAME = 'dev'

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

ASR_CONFIG = {
    'link_labels_blacklist': ['BYOB', 'Customer Owned', 'customer owned']
}
