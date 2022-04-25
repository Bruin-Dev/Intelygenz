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

ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']
CURRENT_ENVIRONMENT = os.environ['CURRENT_ENVIRONMENT']

TIMEZONE = os.environ['TIMEZONE']

PRODUCT_CATEGORY = os.environ['MONITORED_PRODUCT_CATEGORY']

ENABLE_TRIAGE_MONITORING = bool(int(os.environ['ENABLE_TRIAGE_MONITORING']))

if ENABLE_TRIAGE_MONITORING:
    TRIAGE_CONFIG = {
        'polling_minutes': int(os.environ['TRIAGE__MONITORING_JOB_INTERVAL']) // 60,
        'event_limit': int(os.environ['TRIAGE__MAX_EVENTS_PER_EVENT_NOTE']),
        'velo_filter': {},
        'velo_hosts': json.loads(os.environ['TRIAGE__MONITORED_VELOCLOUD_HOSTS']),
        'multiplier': 5,
        'min': 5,
        'stop_delay': 300,
        'semaphore': 1,
    }
else:
    VELOCLOUD_HOST = os.environ['MONITORING__VELOCLOUD_HOST']
    METRICS_RELEVANT_CLIENTS = json.loads(os.environ['METRICS_RELEVANT_CLIENTS'])
    IPA_SYSTEM_USERNAME_IN_BRUIN = os.environ['IPA_SYSTEM_USERNAME_IN_BRUIN']
    MONITOR_CONFIG = {
        'multiplier': 5,
        'min': 5,
        'stop_delay': 300,
        'recipient': os.environ["MONITORING__MISSING_EDGES_FROM_CACHE_REPORT_RECIPIENT"],
        'jobs_intervals': {
            'outage_monitor': int(os.environ['MONITORING__MONITORING_JOB_INTERVAL']),
            'forward_to_hnoc_edge_down': 1,
        },
        'quarantine': {
            Outages.LINK_DOWN: int(os.environ['MONITORING__QUARANTINE_FOR_EDGES_IN_LINK_DOWN_OUTAGE']),
            Outages.HARD_DOWN: int(os.environ['MONITORING__QUARANTINE_FOR_EDGES_IN_HARD_DOWN_OUTAGE']),
            Outages.HA_LINK_DOWN: int(os.environ['MONITORING__QUARANTINE_FOR_EDGES_IN_HA_LINK_DOWN_OUTAGE']),
            Outages.HA_SOFT_DOWN: int(os.environ['MONITORING__QUARANTINE_FOR_EDGES_IN_HA_SOFT_DOWN_OUTAGE']),
            Outages.HA_HARD_DOWN: int(os.environ['MONITORING__QUARANTINE_FOR_EDGES_IN_HA_HARD_DOWN_OUTAGE']),
        },
        'velocloud_instances_filter': {
            VELOCLOUD_HOST: [],
        },
        'blacklisted_link_labels_for_hnoc_forwards': json.loads(
            os.environ['MONITORING__LINK_LABELS_BLACKLISTED_IN_HNOC_FORWARDS']),
        'blacklisted_link_labels_for_asr_forwards': json.loads(
            os.environ['MONITORING__LINK_LABELS_BLACKLISTED_IN_ASR_FORWARDS']),
        'blacklisted_edges': json.loads(os.environ['MONITORING__BLACKLISTED_EDGES']),
        'forward_link_outage_seconds': 60 * 60,
        'last_digi_reboot_seconds': int(os.environ['MONITORING__GRACE_PERIOD_BEFORE_ATTEMPTING_NEW_DIGI_REBOOTS']),
        'semaphore': 5,
        'severity_by_outage_type': {
            'edge_down': int(os.environ['MONITORING__SEVERITY_FOR_EDGE_DOWN_OUTAGES']),
            'link_down': int(os.environ['MONITORING__SEVERITY_FOR_LINK_DOWN_OUTAGES']),
        },
        'autoresolve': {
            'day_schedule': {
                'start_hour': int(os.environ['MONITORING__AUTORESOLVE_DAY_START_HOUR']),
                'end_hour': int(os.environ['MONITORING__AUTORESOLVE_DAY_END_HOUR'])
            },
            'last_outage_seconds': {
                'day': int(os.environ['MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME']),
                'night': int(
                    os.environ['MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME'])
            },
            'max_autoresolves': int(os.environ['MONITORING__MAX_AUTORESOLVES_PER_TICKET']),
        },
    }

LOG_CONFIG = {
    'name': 'service-outage-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-service-outage-monitor'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'service-outage-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090,
}
