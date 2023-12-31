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

LOG_CONFIG = {
    "name": "base-microservice",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": True if os.getenv("PAPERTRAIL_ACTIVE") == "true" else False,
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-base-microservice"),
        "host": os.getenv("PAPERTRAIL_HOST"),
        "port": int(os.getenv("PAPERTRAIL_PORT")),
    },
}

QUART_CONFIG = {"title": "base-microservice", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}
