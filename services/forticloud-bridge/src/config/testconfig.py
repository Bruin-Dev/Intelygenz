# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
}

TIMEZONE = "US/Eastern"

FORTICLOUD_CONFIG = {
    "base_url": "base_url",
    "client_id": "client_id",
    "username": "username",
    "password": "password",
}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

AIOHTTP_CONFIG = {"tracers": []}

METRICS_SERVER_CONFIG = {"port": 9090}
