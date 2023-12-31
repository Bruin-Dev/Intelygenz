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

TIMEZONE = os.environ["TIMEZONE"]

DIGI_CONFIG = {
    "base_url": os.environ["DIGI_BASE_URL"],
    "client_id": os.environ["DIGI_CLIENT_ID"],
    "client_secret": os.environ["DIGI_CLIENT_SECRET"],
    "login_ttl": int(os.environ["DIGI_TOKEN_TTL"]) // 60,
}

ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")

LOG_CONFIG = {
    "name": "digi-bridge",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-digi-bridge"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "digi-bridge", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
