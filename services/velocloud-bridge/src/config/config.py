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


def parse_velocloud_credentials():
    credential_blocks = os.environ["VELOCLOUD_CREDENTIALS"].split(";")
    all_credentials = [credential_block.split("+") for credential_block in credential_blocks]

    return {credentials[0]: {"username": credentials[1], "password": credentials[2]} for credentials in all_credentials}


TIMEZONE = os.environ["TIMEZONE"]

VELOCLOUD_CONFIG = {
    "verify_ssl": True,
    "credentials": parse_velocloud_credentials(),
    "login_interval": 60 * 60 * 23,
}

ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

LOG_CONFIG = {
    "name": "velocloud-bridge",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-velocloud-bridge"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "velocloud-bridge", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
