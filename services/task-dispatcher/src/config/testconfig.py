# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

QUART_CONFIG = {"title": "task-dispatcher", "port": 5000}

CURRENT_ENVIRONMENT = "dev"
ENVIRONMENT_NAME = "dev"

TIMEZONE = "US/Eastern"

DISPATCH_CONFIG = {
    "interval": 60,
}

METRICS_SERVER_CONFIG = {"port": 9090}
