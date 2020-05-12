# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys
import json


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

quarantine_time = 5

MONITOR_MAP_CONFIG = {
    'timezone': 'US/Eastern',
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'refresh_map_time': 60 * 4,
    'blacklisted_edges': [
        # Federal edge that is inside a non-federal Velocloud instance
        {'host': 'mettel.velocloud.net', 'enterprise_id': 170, 'edge_id': 3195}
    ],
    'semaphore': 10,
    'velo_filter': {},
    'environment': os.environ["CURRENT_ENVIRONMENT"],

}

try:
    velocloud_hosts = os.environ["VELOCLOUD_HOSTS"].replace(' ', '').split(':')
    velocloud_hosts_filter = os.environ["VELOCLOUD_HOSTS_FILTER"].replace(' ', '').split(':')
    velocloud_hosts_filter = [json.loads(velo_filter) for velo_filter in velocloud_hosts_filter]
    velocloud_hosts_and_filters = [
        (velocloud_hosts[i], velocloud_hosts_filter[i])
        for i in range(len(velocloud_hosts))
    ]
    velocloud_hosts_and_filters = dict(velocloud_hosts_and_filters)
except Exception as ex:
    print(f"Error loading velocloud hosts and filters {ex}")
    velocloud_hosts_and_filters = {}

MONITOR_CONFIG = {
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    'jobs_intervals': {
        'outage_detector': 60 * 40,
        'outage_monitor': 60 * 3,
        'outage_reporter': 60 * 240,
        'quarantine': quarantine_time,
        'build_cache': 60 * 240
    },
    'quarantine_key_ttl': quarantine_time + 60 * 5,
    # 'velocloud_instances_filter': {
    #    os.environ["VELOCLOUD_HOST"]: [],
    #    "mettel.velocloud.net": [],
    #    "mettel.velocloud1.net": []
    # },
    'velocloud_instances_filter': velocloud_hosts_and_filters,
    'blacklisted_edges': [
        # Federal edge that is inside a non-federal Velocloud instance
        {'host': 'mettel.velocloud.net', 'enterprise_id': 170, 'edge_id': 3195}
    ],
    'autoresolve_down_events_seconds': 45 * 60,
    'semaphore': 10,
    'process_semaphore': 10,
    'events_semaphore': 10,
    'process_errors_semaphore': 10
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
    'send_email': False,
    'polling_minutes': 10,
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'enable_triage': bool(int(os.environ['ENABLE_TRIAGE_MONITORING'])),
    'timezone': 'US/Eastern',
    'monitoring_seconds': 120,
    'event_limit': 15,
    'velo_filter': {},
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'semaphore': 1,
}
