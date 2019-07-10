# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-streaming:4222',
    'cluster_name': 'automation-engine-nats',
    'client_ID': 'edge-monitoring-report-test',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

ALERTS_CONFIG = {
    'edge_monitoring': {
        'recipient': "some.recipient@email.com",
    }
}

QUART_CONFIG = {
    'title': 'edge-monitoring-report',
    'port': 5000
}
