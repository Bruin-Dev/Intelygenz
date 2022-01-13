# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

PRODUCT_CATEGORY = 'SD-WAN'

MONITOR_CONFIG = {
    'monitoring_interval_seconds': 60 * 5,
    'blacklisted_edges': [
        {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
    ],
    'semaphore': 10,
    'velo_filter': {
        "some-host": [],
    },
    'tnba_notes_age_for_new_appends_in_minutes': 30,
    'last_outage_seconds': 60 * 60,
    'request_repair_completed_confidence_threshold': 0.75,
}

CURRENT_ENVIRONMENT = 'dev'

ENVIRONMENT_NAME = "dev"

TIMEZONE = 'US/Eastern'

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'tnba-monitor',
    'port': 5000
}
