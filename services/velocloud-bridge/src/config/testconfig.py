# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
}

TIMEZONE = "US/Eastern"

VELOCLOUD_CONFIG = {
    "verify_ssl": True,
    "credentials": {
        "some_host": {
            "username": "some_username",
            "password": "some_password",
        },
    },
    "login_interval": 60,
}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

METRICS_SERVER_CONFIG = {"port": 9090}
