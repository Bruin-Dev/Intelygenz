# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import json
import logging
import os
import sys
from application import AffectingTroubles

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

PRODUCT_CATEGORY = os.environ['MONITORED_PRODUCT_CATEGORY']

IPA_SYSTEM_USERNAME_IN_BRUIN = os.environ['IPA_SYSTEM_USERNAME_IN_BRUIN']

MONITOR_CONFIG = {
    'monitoring_interval_seconds': int(os.environ['MONITORING_JOB_INTERVAL']),
    'blacklisted_edges': json.loads(os.environ['BLACKLISTED_EDGES']),
    'semaphore': 1,
    'velo_filter': {
        host: []
        for host in json.loads(os.environ['MONITORED_VELOCLOUD_HOSTS'])
    },
    'service_affecting': {
        'metrics_lookup_interval_minutes': int(os.environ['SERVICE_AFFECTING__AUTORESOLVE_LOOKUP_INTERVAL']) // 60,
        'thresholds': {
            # milliseconds
            AffectingTroubles.LATENCY: int(os.environ['SERVICE_AFFECTING__LATENCY_MONITORING_THRESHOLD']),
            # packets
            AffectingTroubles.PACKET_LOSS: int(os.environ['SERVICE_AFFECTING__PACKET_LOSS_MONITORING_THRESHOLD']),
            # milliseconds
            AffectingTroubles.JITTER: int(os.environ['SERVICE_AFFECTING__JITTER_MONITORING_THRESHOLD']),
            # percentage of total bandwidth
            AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
                os.environ['SERVICE_AFFECTING__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD']),
            # number of down / dead events
            AffectingTroubles.BOUNCING: int(os.environ['SERVICE_AFFECTING__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD']),
        },
        'monitoring_minutes_per_trouble': {
            AffectingTroubles.BOUNCING: int(
                os.environ['SERVICE_AFFECTING__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL']) // 60,
        }
    },
    'tnba_notes_age_for_new_appends_in_minutes': int(os.environ['GRACE_PERIOD_BEFORE_APPENDING_NEW_TNBA_NOTES']) // 60,
    'last_outage_seconds': int(os.environ['GRACE_PERIOD_BEFORE_MONITORING_TICKETS_BASED_ON_LAST_DOCUMENTED_OUTAGE']),
    'request_repair_completed_confidence_threshold': int(
        os.environ['MIN_REQUIRED_CONFIDENCE_FOR_REQUEST_AND_REPAIR_COMPLETED_PREDICTIONS']) / 100,
}


TIMEZONE = os.environ['TIMEZONE']

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

LOG_CONFIG = {
    'name': 'tnba-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-tnba-monitor'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'tnba-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}
