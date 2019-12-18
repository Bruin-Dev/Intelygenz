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

TRIAGE_CONFIG = {
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'polling_minutes': 10,
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'timezone': 'US/Eastern',
    'monitoring_seconds': 120,
    'event_limit': 15,
    #   ["VCE20000000940", "VCE20000000895", "VC05200026138", "VC05400001485",
    #   "VC05400001548", "VC05200033081", "VC05200037161", "VC05200059766",
    #   "VC05200033383", "VC05200029594", "VC05200039471", "VC05200038423",
    #   "VC05200043210", "VC05200037717", "VC05200035930", "VC05200037185",
    #   "VC05200033420", "VC05200029665", "VC05200030367", "VC05200033602"
    #   "VC05200037434", "VC05200051358", "VC05200037311", "VC05200033505",
    #   "VC05200037577", "VC05200036898", "VC05200037154", "VC05200037223",
    #   "VC05200037433", "VC05200051251", "VC05200048970"," VC05200038689",
    #   "VC05200037059"]
    #  ['VCE20000000895', 'VC05400001548'] are backup devices for the ones the share velocloud ids with
    'id_by_serial': {
        # Titan America Edges
        "VC05200026138": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 958
        },
        "VC05400001485": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1502
        },
        "VC05400001548": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1502
        },
        "VC05200033081": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1515
        },
        "VC05200029594": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1573
        },
        "VC05200033383": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651
        },
        "VC05200038423": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1997
        },
        "VC05200037161": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2135
        },
        "VC05200039471": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2151
        },
        "VCE20000000940": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2419
        },
        "VCE20000000895": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2419
        },
        "VC05200059766": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2839
        },
        "VC05200043210": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2969
        },
        'VC05200037717': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2279
        },
        'VC05200035930': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2113
        },
        'VC05200037185': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2122
        },
        'VC05200033420': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1743
        },
        'VC05200029665': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1606
        },
        'VC05200030367': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1742
        },
        'VC05200033602': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1747
        },
        'VC05200037434': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1776
        },
        'VC05200051358': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1601
        },
        'VC05200037311': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1996
        },
        'VC05200033505': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1754
        },
        'VC05200037577': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2049
        },
        'VC05200036898': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1940
        },
        'VC05200037154': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2046
        },
        'VC05200037223': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2091
        },
        'VC05200037433': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2048
        },
        'VC05200051251': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2529
        },
        'VC05200048970': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2520
        },
        'VC05200038689': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2132
        },
        'VC05200037059': {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2124
        },
        # Other Edges
        "VC05400002265": {
            "host": "metvco02.mettel.net",
            "enterprise_id": 1,
            "edge_id": 4784
        }
    }

}
LOG_CONFIG = {
    'name': 'service-outage-triage',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'service-outage-triage',
    'port': 5000
}
