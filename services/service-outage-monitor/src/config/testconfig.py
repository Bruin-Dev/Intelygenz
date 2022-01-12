# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

from application import Outages


NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

SEVERITY_LEVELS = {
    'high': 1,
    'medium_high': 2,
    'medium_low': 3,
    'low': 4,
}

ENVIRONMENT_NAME = "dev"
CURRENT_ENVIRONMENT = "dev"

TIMEZONE = 'US/Eastern'

PRODUCT_CATEGORY = 'SD-WAN'

MONITOR_CONFIG = {
    'multiplier': 1,
    'min': 1,
    'stop_delay': 0,
    'recipient': "some.recipient@email.com",
    'jobs_intervals': {
        'outage_monitor': 60 * 3,
        'forward_to_hnoc': 60,
    },
    'quarantine': {
        Outages.LINK_DOWN: 5,
        Outages.HARD_DOWN: 5,
        Outages.HA_LINK_DOWN: 5,
        Outages.HA_SOFT_DOWN: 5,
        Outages.HA_HARD_DOWN: 5,
    },
    'velocloud_instances_filter': {
        "some-host": [],
    },
    'blacklisted_link_labels_for_asr_forwards': ['BYOB', 'Customer Owned', 'customer owned', 'PIAB'],
    'blacklisted_edges': [],
    'forward_link_outage_seconds': 60 * 60,
    'autoresolve_last_outage_seconds': 60 * 60,
    'last_digi_reboot_seconds': 30 * 60,
    'semaphore': 1,
    'severity_by_outage_type': {
        'edge_down': SEVERITY_LEVELS['medium_high'],
        'link_down': SEVERITY_LEVELS['medium_low'],
    },
    'max_autoresolves': 3,
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-outage-monitor',
    'port': 5000
}

TRIAGE_CONFIG = {
    'polling_minutes': 10,
    'event_limit': 15,
    'velo_filter': {"mettel.velocloud.net": []},
    'velo_hosts': ["mettel.velocloud.net", "metvco02.mettel.net", "metvco03.mettel.net", "metvco04.mettel.net"],
    'multiplier': 1,
    'min': 1,
    'stop_delay': 0,
    'semaphore': 1,
}
