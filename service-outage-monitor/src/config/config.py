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

OUTAGE_CONTACTS = [
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
    {
        "email": "gclark@titanamerica.com",
        "phone": "757-533-7151",
        "name": "Gary Clark",
        "type": "site"
    },
    {
        "email": "gclark@titanamerica.com",
        "phone": "757-533-7151",
        "name": "Gary Clark",
        "type": "ticket"
    },
    {
        "email": "Jmack@titanamerica.com",
        "phone": "757-858-6597",
        "name": "Jeff Mack",
        "type": "site"
    },
    {
        "email": "Jmack@titanamerica.com",
        "phone": "757-858-6597",
        "name": "Jeff Mack",
        "type": "ticket"
    },
]

MONITORING_EDGES = [
    # Titan America Edges
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 958
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1502
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1502
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1515
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1573
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1651
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1997
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2135
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2151
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2419
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2419
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2839
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2969
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2279
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2113
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2122
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1743
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1606
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1742
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1747
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1776
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1601
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1996
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1754
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2049
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1940
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2046
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2091
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2048
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2529
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2520
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2132
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2124
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2104
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2134
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1791
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2120
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2071
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2589
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 887
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1602
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1172
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1202
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1483
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1540
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1755
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1756
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1757
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1758
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1759
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1760
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1761
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1777
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1780
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1782
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1785
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1792
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1804
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1844
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1846
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1853
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1876
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1896
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1942
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1943
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1946
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1947
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1948
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1965
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1994
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1995
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1998
    },
    {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2007
    },
    # Other Edges
    {
        "host": "metvco02.mettel.net",
        "enterprise_id": 1,
        "edge_id": 4784
    }
]
