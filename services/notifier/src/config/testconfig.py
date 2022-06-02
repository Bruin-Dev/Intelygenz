# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
}

SLACK_CONFIG = {
    "webhook": "https://test-slack.com",
}

EMAIL_DELIVERY_CONFIG = {
    "email": "fake@gmail.com",
    "password": "456",
}

MONITORABLE_EMAIL_ACCOUNTS = {
    "fake@gmail.com": "456",
}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

METRICS_SERVER_CONFIG = {"port": 9090}
