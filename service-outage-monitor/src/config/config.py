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

MONITORING_EDGES = {
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
    'VC05200037159': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2104
    },
    'VC05200037124': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2134
    },
    'VC05200036905': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1791
    },
    'VC05200037060': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2120
    },
    'VC05200036933': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2071
    },
    'VC05200050849': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2589
    },
    'VC05200016715': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 887
    },
    'VC05200028729': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1602
    },
    'VC05200029227': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1172
    },
    'VC05200028614': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1202
    },
    'VC05200027456': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1483
    },
    'VC05200032234': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1540
    },
    'VC05200033462': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1755
    },
    'VC05200037333': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1756
    },
    'VC05200032322': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1757
    },
    'VC05200034112': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1758
    },
    'VC05200032818': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1759
    },
    'VC05200039301': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1760
    },
    'VC05200038733': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1761
    },
    'VC05200037536': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1777
    },
    'VC05200037410': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1780
    },
    'VC05200034046': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1782
    },
    'VC05200037423': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1785
    },
    'VC05200036924': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1792
    },
    'VC05200037063': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1804
    },
    'VC05200016367': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1844
    },
    'VC05200014851': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1846
    },
    'VC05200036927': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1853
    },
    'VC05200037064': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1876
    },
    'VC05200039098': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1896
    },
    'VC05200033092': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1942
    },
    'VC05200037714': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1943
    },
    'VC05200037160': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1946
    },
    'VC05200037698': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1947
    },
    'VC05200037178': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1948
    },
    'VC05200037301': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1965
    },
    'VC05200039051': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1994
    },
    'VC05200036910': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1995
    },
    'VC05200039330': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 1998
    },
    'VC05200037141': {
        "host": "mettel.velocloud.net",
        "enterprise_id": 137,
        "edge_id": 2007
    },
    'VC05200037265': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2153
    },
    'VC05200036954': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2121
    },
    'VC05200036931': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2137
    },
    'VC05200036829': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2065
    },
    'VC05200036706': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2126
    },
    'VC05200037240': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2130
    },
    'VC05200036967': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2136
    },
    'VC05200036791': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2133
    },
    'VC05200037103': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2141
    },
    'VC05200036670': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2069
    },
    'VC05200036960': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2055
    },
    'VC05200036815': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2125
    },
    'VC05200036849': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2105
    },
    'VC05200037088': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2080
    },
    'VC05200036914': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2129
    },
    'VC05200036133': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2131
    },
    'VC05200036912': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2060
    },
    'VC05200037046': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2152
    },
    'VC05200036345': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2123
    },
    'VC05200035668': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2061
    },
    'VC05200037842': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2212
    },
    'VC05200050688': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2588
    },
    'VC05200050975': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2530
    },
    'VC05200049397': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2519
    },
    'VC05200043154': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2494
    },
    'VC05200057818': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2863
    },
    'VC05200059729': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2208
    },
    'VC05200042630': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2495
    },
    'VC05200044090': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2497
    },
    'VC05200048451': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2582
    },
    'VC05200039505': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2252
    },
    'VC05200044130': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2498
    },
    'VC05200049069': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2517
    },
    'VC05200051218': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2533
    },
    'VC05200051036': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2531
    },
    'VC05400011335': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2358
    },
    'VC05200051057': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2532
    },
    'VC05200045077': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2412
    },
    'VC05200044086': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2518
    },
    'VC05200051203': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2590
    },
    'VC05200042079': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2472
    },
    'VC05200044126': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 137,
        'edge_id': 2500
    },
    # Other Edges
    "VC05400002265": {
        "host": "metvco02.mettel.net",
        "enterprise_id": 1,
        "edge_id": 4784
    }
}
