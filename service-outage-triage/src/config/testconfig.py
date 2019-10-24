# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}
TRIAGE_CONFIG = {
    'environment': "dev",
    'recipient': "some.recipient@email.com",
    'id_by_serial': {
        "VC05200026138": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 958
        },
        "VC05400001485": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1502
        }
    }
}
LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-outage-triage',
    'port': 5000
}
