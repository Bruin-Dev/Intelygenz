import json
import logging
import os
import sys

TIMEZONE = os.environ["TIMEZONE"]

ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

QUART_CONFIG = {"title": "forticloud-bridge", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

REDIS_FORTICLOUD_CACHE = {"host": os.environ["REDIS_CUSTOMER_CACHE_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}

MONITORABLE_MANAGEMENTS_STATUSES = json.loads(os.environ["MONITORABLE_MANAGEMENT_STATUSES"])

FORTICLOUD_CACHE_CONFIGURATION = {"time_to_refresh_interval": int(os.environ["TIME_TO_REFRESH_INTERVAL"])}

NATS_CONFIG = {
    "servers": [os.environ["NATS_SERVER1"]],
    "subscriber": {"pending_limits": 65536},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

FORTICLOUD_CONFIG = {
    "base_url": os.environ["FORTICLOUD_BASE_URL"],
    "account_id": os.environ["FORTICLOUD_ACCOUNT_ID"],
    "username": os.environ["FORTICLOUD_USERNAME"],
    "password": os.environ["FORTICLOUD_PASSWORD"],
}

LOG_CONFIG = {
    "name": "forticloud-bridge",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-forticloud-bridge"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}
