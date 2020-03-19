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
    'velocloud_instances_filter': {
        "some-host": [],
    },
    'autoresolve_serials_whitelist': ["VC05400002265"],
    'autoresolve_down_events_seconds': 45 * 60,
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

TRIAGE_CONFIG = {
    'environment': "dev",
    'polling_minutes': 10,
    'recipient': "some.recipient@email.com",
    'timezone': 'US/Eastern',
    'monitoring_seconds': 120,
    'event_limit': 15,
    'velo_filter': {"mettel.velocloud.net": []},
}
