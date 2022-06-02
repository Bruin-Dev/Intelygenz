# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import json
import logging
import os
import sys

NATS_CONFIG = {
    "servers": [os.environ["NATS_SERVER1"]],
    "subscriber": {"pending_limits": 65536},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

TIMEZONE = os.environ["TIMEZONE"]

INTERMAPPER_CONFIG = {
    "monitoring_interval": int(os.environ["MONITORING_JOB_INTERVAL"]),
    "inbox_email": os.environ["OBSERVED_INBOX_EMAIL_ADDRESS"],
    "sender_emails_list": json.loads(os.environ["OBSERVED_INBOX_SENDERS"]),
    "concurrent_email_batches": int(os.environ["MAX_CONCURRENT_EMAIL_BATCHES"]),
    "intermapper_down_events": json.loads(os.environ["MONITORED_DOWN_EVENTS"]),
    "intermapper_up_events": json.loads(os.environ["MONITORED_UP_EVENTS"]),
    "autoresolve": {
        "day_schedule": {
            "start_hour": int(os.environ["AUTORESOLVE_DAY_START_HOUR"]),
            "end_hour": int(os.environ["AUTORESOLVE_DAY_END_HOUR"]),
        },
        "last_outage_seconds": {
            "day": int(os.environ["GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME"]),
            "night": int(os.environ["GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME"]),
        },
        "max_autoresolves": int(os.environ["MAX_AUTORESOLVES_PER_TICKET"]),
        "product_category_list": json.loads(os.environ["WHITELISTED_PRODUCT_CATEGORIES_FOR_AUTORESOLVE"]),
    },
    "dri_parameters": json.loads(os.environ["DRI_PARAMETERS_FOR_PIAB_NOTES"]),
    "events_lookup_days": int(os.environ["EVENTS_LOOKUP_DAYS"]),
    "stop_after_attempt": 5,
    "wait_multiplier": 1,
    "wait_min": 4,
    "wait_max": 10,
}

LOG_CONFIG = {
    "name": "intermapper-outage-monitor",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-intermapper-outage-monitor"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "intermapper-outage-monitor", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
