import logging
import sys

TIMEZONE = "US/Eastern"
METRICS_SERVER_CONFIG = {"port": 9090}

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
}

REDIS_FORTICLOUD_CACHE = {"host": "redis-forticloud-cache"}
MONITORABLE_MANAGEMENTS_STATUSES = ["test"]

FORTICLOUD_CACHE_CONFIGURATION = {"time_to_refresh_interval": 60}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

FORTICLOUD_CONFIG = {
    "base_url": "base_url",
    "client_id": "client_id",
    "username": "username",
    "password": "password",
}
