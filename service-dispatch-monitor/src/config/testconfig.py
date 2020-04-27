# You must replicate the structure of config.py, changing os.environ calls for mock values
import os
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'client_ID': 'service-dispatch-monitor',
    'subscriber': {
        'max_inflight': 6000,
        'pending_limits': 6000
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

DISPATCH_MONITOR_CONFIG = {
    'timezone': 'US/Eastern',
    'jobs_intervals': {
        'dispatch_monitor': 60 * 1
    },
}

LOG_CONFIG = {
    'name': 'service-dispatch-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}
