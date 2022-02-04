# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys
import json

from application import Outages

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'subscriber': {
        'pending_limits': 65536
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

SEVERITY_LEVELS = {
    'high': 1,
    'medium_high': 2,
    'medium_low': 3,
    'low': 4,
}

quarantine_time = 60 * 3


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
    logging.error(f"Error loading velocloud hosts and filters: {ex}")
    sys.exit(1)

MONITOR_CONFIG = {
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    'jobs_intervals': {
        'outage_monitor': 60 * 10,
        'build_cache': 60 * 240,
        'forward_to_hnoc': 60,
    },
    'quarantine': {
        Outages.LINK_DOWN: quarantine_time,
        Outages.HARD_DOWN: quarantine_time,
        Outages.HA_LINK_DOWN: quarantine_time,
        Outages.HA_SOFT_DOWN: quarantine_time,
        Outages.HA_HARD_DOWN: quarantine_time,
    },
    'velocloud_instances_filter': velocloud_hosts_and_filters,
    'blacklisted_link_labels_for_asr_forwards': ['BYOB', 'Customer Owned', 'customer owned', 'PIAB'],
    'blacklisted_edges': [
        # Federal edge that is inside a non-federal Velocloud instance
        {'host': 'mettel.velocloud.net', 'enterprise_id': 170, 'edge_id': 3195}
    ],
    'forward_link_outage_seconds': 60 * 60,
    'autoresolve_ticket_creation_seconds': 75 * 60,
    'autoresolve_last_outage_seconds': 90 * 60,
    'last_digi_reboot_seconds': 30 * 60,
    'semaphore': 5,
    'severity_by_outage_type': {
        'edge_down': SEVERITY_LEVELS['medium_high'],
        'link_down': SEVERITY_LEVELS['medium_low'],
    },
}

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'service-outage-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-service-outage-monitor'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
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
    'enable_triage': bool(int(os.environ['ENABLE_TRIAGE_MONITORING'])),
    'timezone': 'US/Eastern',
    'monitoring_seconds': 120,
    'event_limit': 15,
    'velo_filter': {},
    'velo_hosts': ["mettel.velocloud.net", "metvco02.mettel.net", "metvco03.mettel.net", "metvco04.mettel.net"],
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'semaphore': 1,
}

METRICS_SERVER_CONFIG = {
    'port': 9090,
}
