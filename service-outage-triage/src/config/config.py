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
    'id_by_serial': ["VCE20000000940", "VCE20000000895", "VC05200026138", "VC05400001485",
                     "VC05400001548", "VC05200033081", "VC05200037161", "VC05200059766",
                     "VC05200033383", "VC05200029594", "VC05200039471", "VC05200038423",
                     "VC05200043210", "VC05200037717", "VC05200035930", "VC05200037185",
                     "VC05200033420", "VC05200029665", "VC05200030367", "VC05200033602",
                     "VC05200037434", "VC05200051358", "VC05200037311", "VC05200033505",
                     "VC05200037577", "VC05200036898", "VC05200037154", "VC05200037223",
                     "VC05200037433", "VC05200051251", "VC05200048970", "VC05200038689",
                     "VC05200037059", "VC05200037159", "VC05200037124", "VC05200036905",
                     "VC05200037060", "VC05200036933", "VC05200050849", "VC05200016715",
                     "VC05200028729", "VC05200029227", "VC05200028614", "VC05200027456",
                     "VC05200032234", "VC05200033462", "VC05200037333", "VC05200032322",
                     "VC05200034112", "VC05200032818", "VC05200039301", "VC05200038733",
                     "VC05200037536", "VC05200037410", "VC05200034046", "VC05200037423",
                     "VC05200036924", "VC05200037063", "VC05200016367", "VC05200014851",
                     "VC05200036927", "VC05200037064", "VC05200039098", "VC05200033092",
                     "VC05200037714", "VC05200037160", "VC05200037698", "VC05200037178",
                     "VC05200037301", "VC05200039051", "VC05200036910", "VC05200039330",
                     "VC05200037141", "VC05200036960", "VC05200036912", "VC05200035668",
                     "VC05200036829", "VC05200036670", "VC05200037088", "VC05200036849",
                     "VC05200036954", "VC05200036345", "VC05200036815", "VC05200036706",
                     "VC05200036914", "VC05200037240", "VC05200036133", "VC05200036791",
                     "VC05200036967", "VC05200036931", "VC05200037103", "VC05200037046",
                     "VC05200037265", "VC05200059729", "VC05200037842", "VC05200039505",
                     "VC05400011335", "VC05200045077", "VC05200042079", "VC05200043154",
                     "VC05200042630", "VC05200044090", "VC05200044130", "VC05200044126",
                     "VC05200049069", "VC05200044086", "VC05200049397", "VC05200050975",
                     "VC05200051036", "VC05200051057", "VC05200051218", "VC05200048451",
                     "VC05200050688", "VC05200051203", "VC05200057818", "VC05400001257",
                     "VCE08400001789"]
    #  ['VCE20000000895', 'VC05400001548'] are backup devices for the ones the share velocloud ids with
    # 'id_by_serial': {
    #     # Titan America Edges
    #     "VC05200026138": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 958
    #     },
    #     "VC05400001485": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1502
    #     },
    #     "VC05400001548": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1502
    #     },
    #     "VC05200033081": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1515
    #     },
    #     "VC05200029594": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1573
    #     },
    #     "VC05200033383": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1651
    #     },
    #     "VC05200038423": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1997
    #     },
    #     "VC05200037161": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2135
    #     },
    #     "VC05200039471": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2151
    #     },
    #     "VCE20000000940": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2419
    #     },
    #     "VCE20000000895": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2419
    #     },
    #     "VC05200059766": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2839
    #     },
    #     "VC05200043210": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2969
    #     },
    #     'VC05200037717': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2279
    #     },
    #     'VC05200035930': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2113
    #     },
    #     'VC05200037185': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2122
    #     },
    #     'VC05200033420': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1743
    #     },
    #     'VC05200029665': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1606
    #     },
    #     'VC05200030367': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1742
    #     },
    #     'VC05200033602': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1747
    #     },
    #     'VC05200037434': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1776
    #     },
    #     'VC05200051358': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1601
    #     },
    #     'VC05200037311': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1996
    #     },
    #     'VC05200033505': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1754
    #     },
    #     'VC05200037577': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2049
    #     },
    #     'VC05200036898': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1940
    #     },
    #     'VC05200037154': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2046
    #     },
    #     'VC05200037223': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2091
    #     },
    #     'VC05200037433': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2048
    #     },
    #     'VC05200051251': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2529
    #     },
    #     'VC05200048970': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2520
    #     },
    #     'VC05200038689': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2132
    #     },
    #     'VC05200037059': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2124
    #     },
    #     'VC05200037159': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2104
    #     },
    #     'VC05200037124': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2134
    #     },
    #     'VC05200036905': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1791
    #     },
    #     'VC05200037060': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2120
    #     },
    #     'VC05200036933': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2071
    #     },
    #     'VC05200050849': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2589
    #     },
    #     'VC05200016715': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 887
    #     },
    #     'VC05200028729': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1602
    #     },
    #     'VC05200029227': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1172
    #     },
    #     'VC05200028614': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1202
    #     },
    #     'VC05200027456': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1483
    #     },
    #     'VC05200032234': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1540
    #     },
    #     'VC05200033462': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1755
    #     },
    #     'VC05200037333': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1756
    #     },
    #     'VC05200032322': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1757
    #     },
    #     'VC05200034112': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1758
    #     },
    #     'VC05200032818': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1759
    #     },
    #     'VC05200039301': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1760
    #     },
    #     'VC05200038733': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1761
    #     },
    #     'VC05200037536': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1777
    #     },
    #     'VC05200037410': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1780
    #     },
    #     'VC05200034046': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1782
    #     },
    #     'VC05200037423': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1785
    #     },
    #     'VC05200036924': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1792
    #     },
    #     'VC05200037063': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1804
    #     },
    #     'VC05200016367': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1844
    #     },
    #     'VC05200014851': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1846
    #     },
    #     'VC05200036927': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1853
    #     },
    #     'VC05200037064': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1876
    #     },
    #     'VC05200039098': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1896
    #     },
    #     'VC05200033092': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1942
    #     },
    #     'VC05200037714': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1943
    #     },
    #     'VC05200037160': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1946
    #     },
    #     'VC05200037698': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1947
    #     },
    #     'VC05200037178': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1948
    #     },
    #     'VC05200037301': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1965
    #     },
    #     'VC05200039051': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1994
    #     },
    #     'VC05200036910': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1995
    #     },
    #     'VC05200039330': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 1998
    #     },
    #     'VC05200037141': {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 137,
    #         "edge_id": 2007
    #     },
    #     'VC05200037265': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2153
    #     },
    #     'VC05200036954': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2121
    #     },
    #     'VC05200036931': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2137
    #     },
    #     'VC05200036829': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2065
    #     },
    #     'VC05200036706': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2126
    #     },
    #     'VC05200037240': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2130
    #     },
    #     'VC05200036967': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2136
    #     },
    #     'VC05200036791': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2133
    #     },
    #     'VC05200037103': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2141
    #     },
    #     'VC05200036670': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2069
    #     },
    #     'VC05200036960': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2055
    #     },
    #     'VC05200036815': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2125
    #     },
    #     'VC05200036849': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2105
    #     },
    #     'VC05200037088': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2080
    #     },
    #     'VC05200036914': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2129
    #     },
    #     'VC05200036133': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2131
    #     },
    #     'VC05200036912': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2060
    #     },
    #     'VC05200037046': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2152
    #     },
    #     'VC05200036345': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2123
    #     },
    #     'VC05200035668': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2061
    #     },
    #     'VC05200037842': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2212
    #     },
    #     'VC05200050688': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2588
    #     },
    #     'VC05200050975': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2530
    #     },
    #     'VC05200049397': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2519
    #     },
    #     'VC05200043154': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2494
    #     },
    #     'VC05200057818': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2863
    #     },
    #     'VC05200059729': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2208
    #     },
    #     'VC05200042630': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2495
    #     },
    #     'VC05200044090': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2497
    #     },
    #     'VC05200048451': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2582
    #     },
    #     'VC05200039505': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2252
    #     },
    #     'VC05200044130': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2498
    #     },
    #     'VC05200049069': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2517
    #     },
    #     'VC05200051218': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2533
    #     },
    #     'VC05200051036': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2531
    #     },
    #     'VC05400011335': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2358
    #     },
    #     'VC05200051057': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2532
    #     },
    #     'VC05200045077': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2412
    #     },
    #     'VC05200044086': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2518
    #     },
    #     'VC05200051203': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2590
    #     },
    #     'VC05200042079': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2472
    #     },
    #     'VC05200044126': {
    #         'host': 'mettel.velocloud.net',
    #         'enterprise_id': 137,
    #         'edge_id': 2500
    #     },
    #     # Other Edges
    #     "VC05400002265": {
    #         "host": "metvco02.mettel.net",
    #         "enterprise_id": 1,
    #         "edge_id": 4784
    #     },
    #     # Marwood edges
    #
    #     "VC05400001257": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 193,
    #         "edge_id": 1614
    #     },
    #     "VCE08400001789": {
    #         "host": "mettel.velocloud.net",
    #         "enterprise_id": 193,
    #         "edge_id": 1616
    #     },
    # }
    'bruin_company_ids': [
        # Titan America
        85940,
        # Mettel
        9994,
        # Marwood
        85100,
        # Sunland logistics
        87030],
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
        # Other Edges (Mettel itself)
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
