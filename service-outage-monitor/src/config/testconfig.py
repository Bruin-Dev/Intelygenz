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
    }
}

quarantine_time = 60 * 10
MONITOR_CONFIG = {
    'recipient': "some.recipient@email.com",
    'environment': "dev",
    'timezone': "US/Eastern",
    'jobs_intervals': {
        'outage_detector': 60 * 40,
        'outage_monitor': 60 * 3,
        'outage_reporter': 60 * 60,
        'quarantine': quarantine_time,
    },
    'quarantine_key_ttl': quarantine_time + 60 * 5,
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-outage-monitor',
    'port': 5000
}

MONITORING_EDGES = {
    'VC0123456789': {
        'host': 'dummy.host.com',
        'enterprise_id': 123,
        'edge_id': 456,
    }
}
