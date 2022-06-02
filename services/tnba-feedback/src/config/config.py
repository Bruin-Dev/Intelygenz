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

PRODUCT_CATEGORY = os.environ["MONITORED_PRODUCT_CATEGORY"]

TNBA_FEEDBACK_CONFIG = {
    "monitoring_interval_seconds": int(os.environ["FEEDBACK_JOB_INTERVAL"]),
    "semaphore": 1,
    "redis_ttl": int(os.environ["GRACE_PERIOD_BEFORE_RESENDING_TICKETS"]),
    "velo_filter": {host: [] for host in json.loads(os.environ["MONITORED_VELOCLOUD_HOSTS"])},
}

LOG_CONFIG = {
    "name": "tnba-feedback",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-tnba-feedback"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "tnba-feedback", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

REDIS_TNBA_FEEDBACK = {"host": os.environ["REDIS_TNBA_FEEDBACK_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
