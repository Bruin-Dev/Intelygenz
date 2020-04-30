# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

MONITOR_CONFIG = {
    'refresh_map_time': 60 * 4,
    'blacklisted_edges': [
        {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
    ],
    'semaphore': 10,
    'velo_filter': {
        "some-host": [],
    },
    'tnba_notes_age_for_new_appends_in_minutes': 30,
}

ENVIRONMENT = 'dev'

TIMEZONE = 'US/Eastern'

MONITORING_INTERVAL_SECONDS = 60 * 20

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

GRAFANA_CONFIG = {
    'port': 9090
}

QUART_CONFIG = {
    'title': 'tnba-monitor',
    'port': 5000
}
