# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys
import os

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

MONITOR_MAP_CONFIG = {
    'timezone': 'US/Eastern',
    'multiplier': 2,
    'min': 2,
    'stop_delay': 2,
    'refresh_map_time': 60 * 1,
    'semaphore': 1,
    'blacklisted_edges': [],
    'velo_filter': {},
    'environment': os.environ.get("CURRENT_ENVIRONMENT", "dev"),
}

MONITOR_CONFIG = {
    'multiplier': 1,
    'min': 1,
    'stop_delay': 0,
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
    'blacklisted_edges': [],
    'autoresolve_down_events_seconds': 45 * 60,
    'semaphore': 1,
    'process_semaphore': 1,
    'events_semaphore': 1
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
    'send_email': True,
    'recipient': "some.recipient@email.com",
    'timezone': 'US/Eastern',
    'monitoring_seconds': 120,
    'event_limit': 15,
    'velo_filter': {"mettel.velocloud.net": []},
    'multiplier': 1,
    'min': 1,
    'stop_delay': 0,
    'semaphore': 1,
}
