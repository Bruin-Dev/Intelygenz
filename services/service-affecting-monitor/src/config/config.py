# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

from application import AffectingTroubles
from config import contact_info

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'subscriber': {
        'pending_limits': 65536
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

MONITOR_CONFIG = {
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'contact_by_host_and_client_id': contact_info.contact_by_host_and_client_id,
    'velo_filter': {
        'mettel.velocloud.net': [],
        'metvco02.mettel.net': [],
        'metvco03.mettel.net': [],
        'metvco04.mettel.net': []
    },
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    'monitoring_minutes_interval': 10,
    'thresholds': {
        AffectingTroubles.LATENCY: 140,                    # milliseconds
        AffectingTroubles.PACKET_LOSS: 8,                  # packets
        AffectingTroubles.JITTER: 50,                      # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 80,  # percentage of total bandwidth
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
        'last_affecting_trouble_seconds': 90 * 60,
        'max_autoresolves': 3,
        'thresholds': {
            AffectingTroubles.BOUNCING: 4,
        }
    },
}

MONITOR_REPORT_CONFIG = {
    'exec_on_start': os.environ['EXEC_MONITOR_REPORTS_ON_START'].lower() == 'true',
    'environment': os.environ['CURRENT_ENVIRONMENT'],
    'timezone': 'US/Eastern',
    'semaphore': 5,
    'wait_fixed': 15,
    'stop_after_attempt': 3,
    'crontab': '0 3 * * 0',
    'threshold': 3,
    'active_reports': ['Jitter', 'Latency', 'Packet Loss', 'Bandwidth Over Utilization'],
    'trailing_days': 14,
    'recipients': {
        'default': ['bsullivan@mettel.net', 'jtaylor@mettel.net', 'HNOCleaderteam@mettel.net',
                    'mettel.automation@intelygenz.com'],
        83959: ['clmillsap@oreillyauto.com', 'mgallion2@oreillyauto.com', 'rbodenhamer@oreillyauto.com',
                'tkaufmann@oreillyauto.com', 'mgoldstein@mettel.net', 'dshim@mettel.net'],
        72959: ['DL_Tenet_Telecom@nttdata.com', 'Jake.Salas@tenethealth.com', 'dshim@mettel.net',
                'mgoldstein@mettel.net'],
        83109: ['JIngwersen@republicservices.com', 'LRozendal@republicservices.com', 'bsherman@mettel.net'],
        86937: ['networkservices@signetjewelers.com', 'pallen@mettel.net'],
        85940: ['ta-infrastructure@titanamerica.com'],
    }
}

BANDWIDTH_REPORT_CONFIG = {
    'exec_on_start': os.environ['EXEC_BANDWIDTH_REPORTS_ON_START'].lower() == 'true',
    'environment': os.environ['CURRENT_ENVIRONMENT'],
    'timezone': 'US/Eastern',
    'crontab': '0 4 * * *',
    'lookup_interval_hours': 24,
    'clients': [86937],
    'recipients': ['bsullivan@mettel.net', 'efox@mettel.net', 'mettel.automation@intelygenz.com']
}

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'service-affecting-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-service-affecting-monitor'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'service-affecting-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}

VELOCLOUD_HOSTS = contact_info.contact_by_host_and_client_id.keys()

ASR_CONFIG = {
    'link_labels_blacklist': ['BYOB', 'Customer Owned', 'customer owned']
}
