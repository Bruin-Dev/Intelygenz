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

ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

TIMEZONE = os.environ["TIMEZONE"]

REPORT_CONFIG = {
    "recipient": os.environ["RECIPIENT"],
    "monitored_velocloud_hosts": json.loads(os.environ["MONITORED_VELOCLOUD_HOSTS"]),
}

LOG_CONFIG = {
    "name": "last-contact-report",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-last-contact-report"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "last-contact-report", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
