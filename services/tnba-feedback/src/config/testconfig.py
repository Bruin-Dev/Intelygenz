# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import os
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
    "multiplier": 0.1,
    "min": 0,
    "stop_delay": 0.1,
    "reconnects": 0,
}

CURRENT_ENVIRONMENT = "dev"
ENVIRONMENT_NAME = "dev"

TIMEZONE = "US/Eastern"

PRODUCT_CATEGORY = "SD-WAN2"

TNBA_FEEDBACK_CONFIG = {
    "environment": "dev",
    "monitoring_interval_seconds": 60 * 60,
    "semaphore": 1,
    # 7 days in seconds
    "redis_ttl": 604800,
    "velo_filter": {"mettel.velocloud.net": []},
}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

QUART_CONFIG = {"title": "tnba-feedback", "port": 5000}

REDIS = {"host": "redis"}

METRICS_SERVER_CONFIG = {"port": 9090}
