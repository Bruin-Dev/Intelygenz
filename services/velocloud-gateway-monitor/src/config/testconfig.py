# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

ENVIRONMENT_NAME = "dev"
CURRENT_ENVIRONMENT = "dev"

TIMEZONE = "US/Eastern"

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

QUART_CONFIG = {"title": "velocloud-gateway-monitor", "port": 5000}

METRICS_SERVER_CONFIG = {"port": 9090}

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
    "multiplier": 1,
    "min": 1,
    "stop_delay": 0,
}

MONITOR_CONFIG = {
    "multiplier": 1,
    "min": 1,
    "stop_delay": 0,
    "monitoring_job_interval": 60,
    "monitored_velocloud_hosts": ["mettel.velocloud.net"],
    "gateway_lookup_intervals": {
        "first_lookup": 3600,
        "second_lookup": 300,
    },
    "thresholds": {
        "tunnel_count": 20,
    },
}
