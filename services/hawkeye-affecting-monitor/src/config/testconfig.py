# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "multiplier": 1,
    "min": 1,
    "stop_delay": 600,
    "reconnects": 150,
}

TIMEZONE = "US/Eastern"

MONITOR_CONFIG = {
    "multiplier": 1,
    "min": 1,
    "stop_delay": 0,
    "environment": "dev",
    "scan_interval": 60 * 15,
    "jobs_intervals": {
        "affecting_monitor": 60 * 15,
    },
    "semaphores": {
        "bruin": 5,
    },
    "product_category": "Network Scout",
}

CURRENT_ENVIRONMENT = "dev"
ENVIRONMENT_NAME = "dev"

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

QUART_CONFIG = {"title": "hawkeye-affecting-monitor", "port": 5000}

REDIS = {"host": "redis-host"}

METRICS_SERVER_CONFIG = {
    "port": 9090,
}
