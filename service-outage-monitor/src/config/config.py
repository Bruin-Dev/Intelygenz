# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'subscriber': {
        'max_inflight': 1,
        'pending_limits': 1
    },
    'publisher': {
        'max_pub_acks_inflight': 1
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

quarantine_time = 30 * 2
MONITOR_CONFIG = {
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    'jobs_intervals': {
        'outage_detector': 30 * 4,
        'outage_monitor': 60 * 3,
        'outage_reporter': 30 * 6,
        'quarantine': quarantine_time,
    },
    'quarantine_key_ttl': quarantine_time + 60 * 5,
}
LOG_CONFIG = {
    'name': 'service-outage-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-outage-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}

OUTAGE_CONTACTS = {
    "VC05400002265": [
        {
            "email": "ndimuro@mettel.net",
            "phone": "732-837-9570",
            "name": "Nicholas Di Muro",
            "type": "site"
        },
        {
            "email": "ndimuro@mettel.net",
            "phone": "732-837-9570",
            "name": "Nicholas Di Muro",
            "type": "ticket"
        },
    ],
    "VC05400001257": [
        {
            "email": "rrogers@marwoodgroup.com",
            "phone": "917-9028-237",
            "name": "Randy Rogers",
            "type": "site"
        },
        {
            "email": "rrogers@marwoodgroup.com",
            "phone": "917-9028-237",
            "name": "Randy Rogers",
            "type": "ticket"
        }
    ],
    "VCE08400001789": [
        {
            "email": "rrogers@marwoodgroup.com",
            "phone": "917-9028-237",
            "name": "Randy Rogers",
            "type": "site"
        },
        {
            "email": "rrogers@marwoodgroup.com",
            "phone": "917-9028-237",
            "name": "Randy Rogers",
            "type": "ticket"
        }
    ]
}

MONITORING_EDGES = {

    # Mettel Edge
    "VC05400002265": {
        "host": "metvco02.mettel.net",
        "enterprise_id": 1,
        "edge_id": 4784
    },
    # Marwood edges
    "VC05400001257": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 193,
        "edge_id": 1614
    },
    "VCE08400001789": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 193,
        "edge_id": 1616
    }
}
