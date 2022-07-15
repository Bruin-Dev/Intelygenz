import json
import logging
import os
import sys

ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]
CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]

TIMEZONE = os.environ["TIMEZONE"]

LOG_CONFIG = {
    "name": "gateway-monitor",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-gateway-monitor"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "gateway-monitor", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}

NATS_CONFIG = {
    "servers": [os.environ["NATS_SERVER1"]],
    "subscriber": {"pending_limits": 65536},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

MONITOR_CONFIG = {
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "monitoring_job_interval": int(os.environ["MONITORING_JOB_INTERVAL"]),
    "monitored_velocloud_hosts": json.loads(os.environ["MONITORED_VELOCLOUD_HOSTS"]),
    "gateway_metrics_lookup_interval": int(os.environ["GATEWAY_METRICS_LOOKUP_INTERVAL"]),
    "thresholds": {
        "tunnel_count": int(os.environ["TUNNEL_COUNT_THRESHOLD"]),
    },
}
