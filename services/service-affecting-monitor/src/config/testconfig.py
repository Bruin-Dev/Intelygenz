# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

from application import AffectingTroubles
from config import contact_info

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}
MONITOR_CONFIG = {
    'recipient': "some.recipient@email.com",
    'contact_by_host_and_client_id': contact_info.contact_by_host_and_client_id,
    'velo_filter': {
        'mettel.velocloud.net': [],
        'metvco02.mettel.net': [],
        'metvco03.mettel.net': [],
        'metvco04.mettel.net': []
    },
    'environment': "test",
    'timezone': 'US/Eastern',
    'monitoring_minutes_interval': 10,
    'thresholds': {
        AffectingTroubles.LATENCY: 140,                    # milliseconds
        AffectingTroubles.PACKET_LOSS: 8,                  # packets
        AffectingTroubles.JITTER: 50,                      # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 90,  # percentage of total bandwidth
        AffectingTroubles.BOUNCING: 10,                    # number of down / dead events
    },
    'monitoring_minutes_per_trouble': {
        AffectingTroubles.LATENCY: 30,
        AffectingTroubles.PACKET_LOSS: 30,
        AffectingTroubles.JITTER: 30,
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 30,
        AffectingTroubles.BOUNCING: 60,
    },
    'forward_to_hnoc': 60,
    'autoresolve': {
        'semaphore': 3,
        'metrics_lookup_interval_minutes': 30,
        'last_affecting_trouble_seconds': 75 * 60,
        'max_autoresolves': 3,
        'thresholds': {
            AffectingTroubles.BOUNCING: 4,
        },
    },
}

MONITOR_REPORT_CONFIG = {
    "semaphore": 5,
    'wait_fixed': 1,
    'stop_after_attempt': 2,
    'environment': "test",
    'crontab': '0 8 * * *',
    'client_id_bandwidth': 83109,
    'threshold': 3,
    'active_reports': ['Jitter', 'Latency', 'Packet Loss', 'Bandwidth Over Utilization'],
    'trailing_days': 14,
    'monitoring_minutes_interval': 10,
    'timezone': 'US/Eastern',
    "report_config_by_trouble": {
        'default': ['bsullivan@mettel.net', 'jtaylor@mettel.net', 'HNOCleaderteam@mettel.net',
                    'mettel.automation@intelygenz.com'],
        83959: ['clmillsap@oreillyauto.com', 'mgallion2@oreillyauto.com', 'rbodenhamer@oreillyauto.com',
                'tkaufmann@oreillyauto.com', 'mgoldstein@mettel.net'],
        72959: ['DL_Tenet_Telecom@nttdata.com', 'Jake.Salas@tenethealth.com', 'dshim@mettel.net',
                'mgoldstein@mettel.net'],
        83109: ['JIngwersen@republicservices.com', 'LRozendal@republicservices.com', 'bsherman@mettel.net']
    }
}

ENVIRONMENT_NAME = "dev"

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-affecting-monitor',
    'port': 5000
}

VELOCLOUD_HOSTS = contact_info.contact_by_host_and_client_id.keys()

ASR_CONFIG = {
    'link_labels_blacklist': ['BYOB', 'Customer Owned', 'customer owned']
}
