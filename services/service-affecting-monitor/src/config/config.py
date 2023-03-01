# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import json
import logging
import os
import sys

from application import AffectingTroubles


def parse_client_ids(data_by_host_and_client_id):
    # JSON only allows string keys, but client IDs are ints so we need to parse them before loading the config,
    # except for placeholders that will be replaced by multiple client IDs at run time
    for host in data_by_host_and_client_id:
        data_by_host_and_client_id[host] = {
            int(client_id) if client_id.isnumeric() else client_id: data
            for client_id, data in data_by_host_and_client_id[host].items()
        }
    return data_by_host_and_client_id


NATS_CONFIG = {
    "servers": [os.environ["NATS_SERVER1"]],
    "subscriber": {"pending_limits": 65536},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

TIMEZONE = os.environ["TIMEZONE"]

IPA_SYSTEM_USERNAME_IN_BRUIN = os.environ["IPA_SYSTEM_USERNAME_IN_BRUIN"]

PRODUCT_CATEGORY = os.environ["MONITORED_PRODUCT_CATEGORY"]

VELOCLOUD_HOST = os.environ["MONITORED_VELOCLOUD_HOST"]

UMBRELLA_HOSTS = json.loads(os.environ["UMBRELLA_HOSTS"])

METRICS_RELEVANT_CLIENTS = json.loads(os.environ["METRICS_RELEVANT_CLIENTS"])

MONITOR_CONFIG = {
    "contact_info_by_host_and_client_id": parse_client_ids(
        json.loads(os.environ["MONITORING__DEFAULT_CONTACT_INFO_PER_CUSTOMER"])
    ),
    "customers_to_always_use_default_contact_info": json.loads(
        os.environ["MONITORING__CUSTOMERS_TO_ALWAYS_USE_DEFAULT_CONTACT_INFO"]
    ),
    "velo_filter": {VELOCLOUD_HOST: []},
    "monitoring_minutes_interval": int(os.environ["MONITORING__MONITORING_JOB_INTERVAL"]) // 60,
    "thresholds": {
        AffectingTroubles.LATENCY: int(os.environ["MONITORING__LATENCY_MONITORING_THRESHOLD"]),  # milliseconds
        AffectingTroubles.PACKET_LOSS: int(os.environ["MONITORING__PACKET_LOSS_MONITORING_THRESHOLD"]),  # packets
        AffectingTroubles.JITTER: int(os.environ["MONITORING__JITTER_MONITORING_THRESHOLD"]),  # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
            os.environ["MONITORING__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD"]
        ),  # percentage of total bandwidth
        AffectingTroubles.BOUNCING: int(
            os.environ["MONITORING__CIRCUIT_INSTABILITY_MONITORING_THRESHOLD"]
        ),  # number of down / dead events
    },
    "wireless_thresholds": {
        AffectingTroubles.LATENCY: int(os.environ["MONITORING__WIRELESS_LATENCY_MONITORING_THRESHOLD"]),  # milliseconds
        # packets
        AffectingTroubles.PACKET_LOSS: int(os.environ["MONITORING__WIRELESS_PACKET_LOSS_MONITORING_THRESHOLD"]),
        AffectingTroubles.JITTER: int(os.environ["MONITORING__WIRELESS_JITTER_MONITORING_THRESHOLD"]),  # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
            os.environ["MONITORING__WIRELESS_BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD"]
        ),  # percentage of total bandwidth
        AffectingTroubles.BOUNCING: int(
            os.environ["MONITORING__WIRELESS_CIRCUIT_INSTABILITY_MONITORING_THRESHOLD"]
        ),  # number of down / dead events
    },
    "monitoring_minutes_per_trouble": {
        AffectingTroubles.LATENCY: int(os.environ["MONITORING__LATENCY_MONITORING_LOOKUP_INTERVAL"]) // 60,
        AffectingTroubles.PACKET_LOSS: int(os.environ["MONITORING__PACKET_LOSS_MONITORING_LOOKUP_INTERVAL"]) // 60,
        AffectingTroubles.JITTER: int(os.environ["MONITORING__JITTER_MONITORING_LOOKUP_INTERVAL"]) // 60,
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
            os.environ["MONITORING__BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL"]
        )
        // 60,
        AffectingTroubles.BOUNCING: int(os.environ["MONITORING__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL"]) // 60,
    },
    "wireless_monitoring_minutes_per_trouble": {
        AffectingTroubles.LATENCY: int(os.environ["MONITORING__WIRELESS_LATENCY_MONITORING_LOOKUP_INTERVAL"]) // 60,
        AffectingTroubles.PACKET_LOSS: int(
            os.environ["MONITORING__WIRELESS_PACKET_LOSS_MONITORING_LOOKUP_INTERVAL"]) // 60,
        AffectingTroubles.JITTER: int(os.environ["MONITORING__WIRELESS_JITTER_MONITORING_LOOKUP_INTERVAL"]) // 60,
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
            os.environ["MONITORING__WIRELESS_BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL"]
        )
        // 60,
        AffectingTroubles.BOUNCING: int(
            os.environ["MONITORING__WIRELESS_CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL"]) // 60,
    },
    "blacklisted_link_labels_for_asr_forwards": json.loads(os.environ["LINK_LABELS_BLACKLISTED_FROM_ASR_FORWARDS"]),
    "blacklisted_link_labels_for_hnoc_forwards": json.loads(os.environ["LINK_LABELS_BLACKLISTED_FROM_HNOC_FORWARDS"]),
    "autoresolve": {
        "semaphore": 3,
        "metrics_lookup_interval_minutes": int(os.environ["MONITORING__AUTORESOLVE_LOOKUP_INTERVAL"]) // 60,
        "day_schedule": {
            "start_hour": int(os.environ["MONITORING__AUTORESOLVE_DAY_START_HOUR"]),
            "end_hour": int(os.environ["MONITORING__AUTORESOLVE_DAY_END_HOUR"]),
        },
        "last_affecting_trouble_seconds": {
            "day": int(os.environ["MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_DAY_TIME"]),
            "night": int(
                os.environ["MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_NIGHT_TIME"]
            ),
        },
        "max_autoresolves": int(os.environ["MONITORING__MAX_AUTORESOLVES_PER_TICKET"]),
        "thresholds": {
            AffectingTroubles.BOUNCING: int(os.environ["MONITORING__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD"]),
        },
    },
    "customers_with_bandwidth_enabled": json.loads(
        os.environ["MONITORING__CUSTOMERS_WITH_BANDWIDTH_MONITORING_ENABLED"]
    ),
    "wait_time_before_sending_new_milestone_reminder": int(
        os.environ["MONITORING__WAIT_TIME_BEFORE_SENDING_NEW_MILESTONE_REMINDER"]
    ),
}

MONITOR_REPORT_CONFIG = {
    "exec_on_start": os.environ["EXEC_MONITOR_REPORTS_ON_START"].lower() == "true",
    "semaphore": 5,
    "wait_fixed": 15,
    "stop_after_attempt": 3,
    "crontab": os.environ["REOCCURRING_TROUBLE_REPORT__EXECUTION_CRON_EXPRESSION"],
    "threshold": int(os.environ["REOCCURRING_TROUBLE_REPORT__REOCCURRING_TROUBLE_TICKETS_THRESHOLD"]),
    "active_reports": json.loads(os.environ["REOCCURRING_TROUBLE_REPORT__REPORTED_TROUBLES"]),
    "trailing_days": int(os.environ["REOCCURRING_TROUBLE_REPORT__TICKETS_LOOKUP_INTERVAL"]) // 60 // 60 // 24,
    "default_contacts": json.loads(os.environ["REOCCURRING_TROUBLE_REPORT__DEFAULT_CONTACTS"]),
    "recipients_by_host_and_client_id": parse_client_ids(
        json.loads(os.environ["REOCCURRING_TROUBLE_REPORT__RECIPIENTS_PER_HOST_AND_CUSTOMER"])
    ),
}

BANDWIDTH_REPORT_CONFIG = {
    "exec_on_start": os.environ["EXEC_BANDWIDTH_REPORTS_ON_START"].lower() == "true",
    "environment": os.environ["CURRENT_ENVIRONMENT"],
    "crontab": os.environ["DAILY_BANDWIDTH_REPORT__EXECUTION_CRON_EXPRESSION"],
    "lookup_interval_hours": int(os.environ["DAILY_BANDWIDTH_REPORT__LOOKUP_INTERVAL"]) // 60 // 60,
    "client_ids_by_host": json.loads(os.environ["DAILY_BANDWIDTH_REPORT__ENABLED_CUSTOMERS_PER_HOST"]),
    "recipients": json.loads(os.environ["DAILY_BANDWIDTH_REPORT__RECIPIENTS"]),
    "s3_bucket": os.environ["DAILY_BANDWIDTH_REPORT__S3_BUCKET"],
}

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

LOG_CONFIG = {
    "name": "service-affecting-monitor",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-service-affecting-monitor"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "service-affecting-monitor", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
