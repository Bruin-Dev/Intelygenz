# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
}

CURRENT_ENVIRONMENT = "dev"
ENVIRONMENT_NAME = "dev"

TIMEZONE = "US/Eastern"

FRAUD_CONFIG = {
    "monitoring_interval": 5,
    "inbox_email": "mettel.automation@intelygenz.com",
    "sender_emails_list": ["amate@mettel.net"],
    "default_client_info": {
        "client_id": 9994,
        "service_number": "2126070002",
    },
    "default_contact": {
        "name": "Holmdel NOC",
        "email": "holmdelnoc@mettel.net",
    },
}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

QUART_CONFIG = {"title": "fraud-monitor", "port": 5000}

METRICS_SERVER_CONFIG = {"port": 9090}
