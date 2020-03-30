# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'subscriber': {
        'max_inflight': 1,
        'pending_limits': 1
    },
    'publisher': {
        'max_pub_acks_inflight': 1
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

quarantine_time = 60 * 10

MONITOR_MAP_CONFIG = {
    'timezone': 'US/Eastern',
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'refresh_map_time': 60 * 4,
    'semaphore': 10,
    'velo_filter': {},
    'environment': os.environ["CURRENT_ENVIRONMENT"],

}

MONITOR_CONFIG = {
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    'jobs_intervals': {
        'outage_detector': 60 * 40,
        'outage_monitor': 60 * 3,
        'outage_reporter': 60 * 240,
        'quarantine': quarantine_time,
    },
    'quarantine_key_ttl': quarantine_time + 60 * 5,
    'velocloud_instances_filter': {
        "mettel.velocloud.net": [193, 191, 170, 74, 120],
    },
    'blacklisted_edges': [
        # Federal edge that is inside a non-federal Velocloud instance
        {'host': 'mettel.velocloud.net', 'enterprise_id': 170, 'edge_id': 3195}
    ],
    'autoresolve_down_events_seconds': 45 * 60,
}
LOG_CONFIG = {
    'name': 'service-outage-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-outage-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

TRIAGE_CONFIG = {
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'polling_minutes': 10,
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'timezone': 'US/Eastern',
    'monitoring_seconds': 120,
    'event_limit': 15,
    'velo_filter': {},
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'semaphore': 5,
}
