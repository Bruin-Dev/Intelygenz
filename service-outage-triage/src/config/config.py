# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'cluster_name': os.environ["NATS_CLUSTER_NAME"],
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
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    # TODO Research why there are only 11 of 13 of the serials given after automated process searching for them:
    #   ["VCE20000000940", "VCE20000000895", "VC05200026138", "VC05400001485",
    #   "VC05400001548", "VC05200033081", "VC05200037161", "VC05200059766",
    #   "VC05200033383", "VC05200029594", "VC05200039471", "VC05200038423",
    #   "VC05200043210"]
    # The ones not appearing are ['VCE20000000895', 'VC05400001548']
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
        "VC05200059766": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2839
        },
        "VC05200043210": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 2969
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
