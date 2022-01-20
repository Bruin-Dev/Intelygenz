# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import json
import logging
import os
import sys
from collections import defaultdict

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

# JSON only allows string keys, but client IDs are ints so we need to parse them before loading the config
default_contact_info_raw = json.loads(os.environ['MONITORING__DEFAULT_CONTACT_INFO_PER_CUSTOMER'])
default_contact_info = defaultdict(dict)
for host in default_contact_info.keys():
    default_contact_info.setdefault(host, {})
    for client_id in default_contact_info_raw[host]:
        if client_id.isnumeric():
            default_contact_info[host][int(client_id)] = default_contact_info_raw[host][client_id]
        else:
            # Possibly a placeholder that will be replaced by multiple client IDs at run time, these should remain
            # the same
            default_contact_info[host][client_id] = default_contact_info_raw[host][client_id]

TIMEZONE = os.environ['TIMEZONE']

PRODUCT_CATEGORY = os.environ['MONITORED_PRODUCT_CATEGORY']

MONITOR_CONFIG = {
    'contact_by_host_and_client_id': default_contact_info,
    'velo_filter': {
        host: []
        for host in json.loads(os.environ['MONITORING__MONITORED_VELOCLOUD_HOSTS'])
    },
    'monitoring_minutes_interval': int(os.environ['MONITORING__MONITORING_JOB_INTERVAL']) // 60,
    'thresholds': {
        AffectingTroubles.LATENCY: int(os.environ['MONITORING__LATENCY_MONITORING_THRESHOLD']),          # milliseconds
        AffectingTroubles.PACKET_LOSS: int(os.environ['MONITORING__PACKET_LOSS_MONITORING_THRESHOLD']),  # packets
        AffectingTroubles.JITTER: int(os.environ['MONITORING__JITTER_MONITORING_THRESHOLD']),            # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
            os.environ['MONITORING__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD']),  # percentage of total bandwidth
        AffectingTroubles.BOUNCING: int(
            os.environ['MONITORING__CIRCUIT_INSTABILITY_MONITORING_THRESHOLD']),         # number of down / dead events
    },
    'monitoring_minutes_per_trouble': {
        AffectingTroubles.LATENCY: int(os.environ['MONITORING__LATENCY_MONITORING_LOOKUP_INTERVAL']) // 60,
        AffectingTroubles.PACKET_LOSS: int(os.environ['MONITORING__PACKET_LOSS_MONITORING_LOOKUP_INTERVAL']) // 60,
        AffectingTroubles.JITTER: int(os.environ['MONITORING__JITTER_MONITORING_LOOKUP_INTERVAL']) // 60,
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
            os.environ['MONITORING__BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL']) // 60,
        AffectingTroubles.BOUNCING: int(os.environ['MONITORING__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL']) // 60,
    },
    'forward_to_hnoc': 60,
    'autoresolve': {
        'semaphore': 3,
        'metrics_lookup_interval_minutes': int(os.environ['MONITORING__AUTORESOLVE_LOOKUP_INTERVAL']) // 60,
        'last_affecting_trouble_seconds': int(
            os.environ['MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE']),
        'max_autoresolves': int(os.environ['MONITORING__MAX_AUTORESOLVES_PER_TICKET']),
        'thresholds': {
            AffectingTroubles.BOUNCING: int(os.environ['MONITORING__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD']),
        }
    },
    'customers_with_bandwidth_enabled': json.loads(
        os.environ['MONITORING__CUSTOMERS_WITH_BANDWIDTH_MONITORING_ENABLED']),
}

# JSON only allows string keys, but client IDs are ints so we need to parse them before loading the config
recipients_by_customer_raw = json.loads(os.environ['REOCCURRING_TROUBLE_REPORT__RECIPIENTS_PER_CUSTOMER'])
recipients_by_customer = defaultdict(dict)
for client_id in recipients_by_customer.keys():
    if client_id.isnumeric():
        recipients_by_customer[int(client_id)] = recipients_by_customer_raw[client_id]
    else:
        # Possibly a list of default recipients common to all reports, these should remain the same
        recipients_by_customer[client_id] = recipients_by_customer_raw[client_id]

MONITOR_REPORT_CONFIG = {
    'exec_on_start': os.environ['EXEC_MONITOR_REPORTS_ON_START'].lower() == 'true',
    'semaphore': 5,
    'wait_fixed': 15,
    'stop_after_attempt': 3,
    'crontab': os.environ['REOCCURRING_TROUBLE_REPORT__EXECUTION_CRON_EXPRESSION'],
    'threshold': int(os.environ['REOCCURRING_TROUBLE_REPORT__REOCCURRING_TROUBLE_TICKETS_THRESHOLD']),
    'active_reports': json.loads(os.environ['REOCCURRING_TROUBLE_REPORT__REPORTED_TROUBLES']),
    'trailing_days': int(os.environ['REOCCURRING_TROUBLE_REPORT__TICKETS_LOOKUP_INTERVAL']) // 60 // 60 // 24,
    'recipients': recipients_by_customer,
}

BANDWIDTH_REPORT_CONFIG = {
    'exec_on_start': os.environ['EXEC_BANDWIDTH_REPORTS_ON_START'].lower() == 'true',
    'environment': os.environ['CURRENT_ENVIRONMENT'],
    'crontab': os.environ['DAILY_BANDWIDTH_REPORT__EXECUTION_CRON_EXPRESSION'],
    'lookup_interval_hours': int(os.environ['DAILY_BANDWIDTH_REPORT__LOOKUP_INTERVAL']) // 60 // 60,
    'clients': json.loads(os.environ['DAILY_BANDWIDTH_REPORT__ENABLED_CUSTOMERS']),
    'recipients': json.loads(os.environ['DAILY_BANDWIDTH_REPORT__RECIPIENTS']),
}

CURRENT_ENVIRONMENT = os.environ['CURRENT_ENVIRONMENT']
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']

LOG_CONFIG = {
    'name': 'service-affecting-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': os.environ['PAPERTRAIL_ACTIVE'] == "true",
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-service-affecting-monitor'),
        'host': os.environ['PAPERTRAIL_HOST'],
        'port': int(os.environ['PAPERTRAIL_PORT'])
    },
}

QUART_CONFIG = {
    'title': 'service-affecting-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}

ASR_CONFIG = {
    'link_labels_blacklist': json.loads(os.environ['MONITORING__LINK_LABELS_BLACKLISTED_IN_ASR_FORWARDS']),
}
