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

quarantine_time = 60 * 10
MONITOR_CONFIG = {
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    'jobs_intervals': {
        'outage_detector': 60 * 40,
        'outage_monitor': 60 * 3,
        'outage_reporter': 60 * 60,
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
    },
    # Sunland Logistics edges

    "VC05200033822": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 1579
    },

    "VC05200033292": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 1580
    },

    "VC05200023719": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 1584
    },

    "VC05200032723": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 1586
    },

    "VC05200028945": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 1596
    },

    "VC05400001465": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 1611
    },

    "VC05200035645": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 2057
    },

    "VC05200035383": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 2098
    },

    "VC05200036935": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 2108
    },

    "VC05200016642": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 2948
    },

    "VC05200012781": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 2992
    },

    "VC05200069359": {
        "host": "mettel.velocloud.net",
        "enterprise_id": 191,
        "edge_id": 3169
    },

    # Planet home lending

    'VC05400017787': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2924
    },
    'VC05400018334': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2865
    },
    'VC05200039042': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2413
    },
    'VC05400018645': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2850
    },
    'VC05200039063': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2163
    },
    'VC05200043037': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2392
    },
    'VC05400006773': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2138
    },
    'VCE08400002713': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 3188
    },
    'VC05200056383': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2576
    },
    'VC05200069615': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 3152
    },
    'VC05400012544': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2428
    },
    'VC05400014471': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2675
    },
    'VCE08400000024': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 1610
    },
    'VCE08400002428': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 3195
    },
    'VCE08400003079': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2566
    },
    'VC05100042088': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2663
    },
    'VC05200035353': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2112
    },
    'VCE08400000896': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 1457
    },
    'VCE08400000737': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 1458
    },
    'VC05200044788': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2512
    },
    'VCE08400002115': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 1803
    },
    'VC05400010813': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2383
    },
    'VCE08400002682': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2308
    },
    'VC05200043272': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2259
    },
    'VC05200062803': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2925
    },
    'VC05400011928': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2452
    },
    'VC05400014486': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2656
    },
    'VC05200043505': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2260
    },
    'VC05200038567': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2165
    },
    'VC05400012064': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2429
    },
    'VC05400023946': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2926
    },
    'VCE08400002673': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2325
    },
    'VC05400015426': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2534
    },
    'VC05400014293': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2655
    },
    'VC05400015370': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2674
    },
    'VCE08400001089': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 1382
    },
    'VC05400015392': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2665
    },
    'VC05200045071': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2426
    },
    'VC05400011799': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2369
    },
    'VCE08400004143': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2694
    },
    'VC05400006582': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2115
    },
    'VC05400017307': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2847
    },
    'VC05200038305': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 2164
    },

}
