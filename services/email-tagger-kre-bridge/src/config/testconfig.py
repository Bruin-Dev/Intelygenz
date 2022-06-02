# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import os
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "multiplier": 0.1,
    "min": 0,
    "stop_delay": 0.4,
    "reconnects": 0,
}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

KRE_CONFIG = {"base_url": "http://test-url.com", "grpc_secure_mode": False}

METRICS_SERVER_CONFIG = {"port": 9090}
