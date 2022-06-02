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

TIMEZONE = os.environ["TIMEZONE"]

IPA_SYSTEM_USERNAME_IN_BRUIN = os.environ["IPA_SYSTEM_USERNAME_IN_BRUIN"]

MONITOR_CONFIG = {
    "max_retries_error_404": 5,
    "tag_ids": json.loads(os.environ["TAG_IDS_MAPPING"]),
    "scheduler_config": {
        "repair_ticket_monitor": int(os.environ["RTA_MONITOR_JOB_INTERVAL"]),
        "new_created_tickets_feedback": int(os.environ["NEW_CREATED_TICKETS_FEEDBACK_JOB_INTERVAL"]),
        "new_closed_tickets_feedback": int(os.environ["NEW_CLOSED_TICKETS_FEEDBACK_JOB_INTERVAL"]),
    },
    "nats_request_timeout": {
        "kre_seconds": 30,
        "bruin_request_seconds": 30,
    },
    "semaphores": {
        "repair_tickets_concurrent": int(os.environ["MAX_CONCURRENT_EMAILS_FOR_MONITORING"]),
        "created_tickets_concurrent": int(os.environ["MAX_CONCURRENT_CREATED_TICKETS_FOR_FEEDBACK"]),
        "closed_tickets_concurrent": int(os.environ["MAX_CONCURRENT_CLOSED_TICKETS_FOR_FEEDBACK"]),
    },
}

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

LOG_CONFIG = {
    "name": "repair-tickets-monitor",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-repair-tickets-monitor"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "repair-tickets-automation", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

REDIS_CACHE = {"host": os.environ["REDIS_EMAIL_TAGGER_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
