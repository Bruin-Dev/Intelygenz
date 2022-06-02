# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
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

ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")
CURRENT_ENVIRONMENT = os.getenv("CURRENT_ENVIRONMENT")

SCHEDULER_TIMEZONE = "US/Eastern"
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_URL = os.getenv("MONGO_URL")
MONGO_PORT = os.getenv("MONGO_PORT")
STORING_INTERVAL_MINUTES = 5
VELO_HOST = "mettel.velocloud.net"
ENTERPRISE_ID = 22
ENDPOINT_PREFIX = "/api"

LOG_CONFIG = {
    "name": "links-metrics-api",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.getenv("PAPERTRAIL_ACTIVE") == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-links-metrics-api"),
        "host": os.getenv("PAPERTRAIL_HOST"),
        "port": int(os.getenv("PAPERTRAIL_PORT")),
    },
}

QUART_CONFIG = {"title": "links-metrics-api", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
