# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys
import os

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

quarantine_time = 5

MONITOR_CONFIG = {
    'multiplier': 1,
    'min': 1,
    'stop_delay': 0,
    'recipient': "some.recipient@email.com",
    'environment': "dev",
    'timezone': "US/Eastern",
    'jobs_intervals': {
        'outage_monitor': 60 * 3,
        'quarantine': quarantine_time,
        'build_cache': 60 * 60,
        'forward_to_hnoc': 60,
    },
    'velocloud_instances_filter': {
        "some-host": [],
    },
    'blacklisted_edges': [],
    'forward_link_outage_seconds': 60 * 60,
    'autoresolve_ticket_creation_seconds': 60 * 60,
    'autoresolve_last_outage_seconds': 60 * 60,
    'last_digi_reboot_seconds': 30 * 60,
    'semaphore': 1,
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

ENVIRONMENT_NAME = "dev"

TRIAGE_CONFIG = {
    'environment': "dev",
    'polling_minutes': 10,
    'recipient': "some.recipient@email.com",
    'enable_triage': True,
    'timezone': 'US/Eastern',
    'monitoring_seconds': 120,
    'event_limit': 15,
    'velo_filter': {"mettel.velocloud.net": []},
    'velo_hosts': ["mettel.velocloud.net", "metvco02.mettel.net", "metvco03.mettel.net", "metvco04.mettel.net"],
    'multiplier': 1,
    'min': 1,
    'stop_delay': 0,
    'semaphore': 1,
}
