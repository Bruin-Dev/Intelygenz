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
    'autoresolve_serials_whitelist': [
        # Mettel test edge
        "VC05400002265",
        # Marwood edges
        "VC05400001257",
        "VCE08400001789"
        # Sunland logistics
        'VC05200033822', 'VC05200033292', 'VC05200023719', 'VC05200032723', 'VC05200028945', 'VC05400001465',
        'VC05200035645', 'VC05200035383', 'VC05200036935', 'VC05200016642', 'VC05200012781', 'VC05200069359',
        # Planet home lending
        # Faulty: "VCE08400002428"
        'VC05400017787', 'VC05400018334', 'VC05200039042', 'VC05400018645', 'VC05200039063', 'VC05200043037',
        'VC05400006773', 'VCE08400002713', 'VC05200056383', 'VC05200069615', 'VC05400012544', 'VC05400014471',
        'VCE08400000024', 'VCE08400003079', 'VC05100042088', 'VC05200035353', 'VCE08400000896',
        'VCE08400000737', 'VC05200044788', 'VCE08400002115', 'VC05400010813', 'VCE08400002682', 'VC05200043272',
        'VC05200062803', 'VC05400011928', 'VC05400014486', 'VC05200043505', 'VC05200038567', 'VC05400012064',
        'VC05400023946', 'VCE08400002673', 'VC05400015426', 'VC05400014293', 'VC05400015370', 'VCE08400001089',
        'VC05400015392', 'VC05200045071', 'VC05400011799', 'VCE08400004143', 'VC05400006582', 'VC05400017307',
        'VC05200038305'

    ],
    'bruin_company_ids': [
        # Titan America
        85940,
        # Mettel
        9994,
        # Marwood
        85100,
        # Sunland logistics
        87030,
        # Planet home lending
        86692,
        # Familia health
        85987,
        # Vineyard Vines
        84816,
        # Le Duff
        84701
    ],
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

        # Familia health
        'VC05100050058': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2734
        },
        'VC05200043698': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2273
        },
        'VC05200044799': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2418
        },
        'VCE08400005358': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2974
        },
        'VC05200030750': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2979
        },
        'VC05200013093': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2977
        },
        'VC05100050542': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2754
        },
        'VC05100037867': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2937
        },
        'VC05100005736': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2456
        },
        'VC00006387': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 456
        },
        'VC05100050636': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2753
        },
        'VC05200035420': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1808
        },
        'VC05200050962': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2535
        },
        'VC05200025712': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1852
        },
        'VC05200025858': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1817
        },
        'VC00006483': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 412
        },
        'VC05200025993': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1811
        },
        'VC00006487': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 322
        },
        'VC00006677': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 452
        },
        'VC05200025718': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1816
        },
        'VC05100010741': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2458
        },
        'VC05200009868': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 469
        },
        'VC05100005777': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2454
        },
        'VC05100050256': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2733
        },
        'VC05200027330': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1809
        },
        'VC05200029438': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1500
        },
        'VC05200056131': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 3020
        },
        'VC05200058778': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2923
        },
        'VC05100009902': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2351
        },
        'VC05100015061': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2414
        },
        'VC00000455': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2003
        },
        'VC05200038404': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2086
        },
        'VC05200025788': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1814
        },
        'VC05100049912': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2892
        },
        'VC05200024848': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1818
        },
        'VC05100020484': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2536
        },
        'VC05100011001': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2364
        },
        'VC05200012003': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 472
        },
        'VC05200025522': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1813
        },
        'VC05200011116': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1810
        },
        'VC05100024269': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2459
        },
        'VC05100041018': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2601
        },
        'VC05200027081': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1850
        },
        'VC05200026330': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1812
        },
        'VC05100026734': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2455
        },
        'VC05200008978': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 496
        },
        'VC05200025705': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2433
        },
        'VC00006495': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 573
        },
        'VC05100042279': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2732
        },
        'VC05200014645': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1851
        },
        'VC05100010740': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2460
        },
        'VC05200045072': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2462
        },
        'VC05200029048': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1485
        },
        'VC05200009111': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1482
        },
        'VC00006373': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 453
        },
        'VC05100042887': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2602
        },
        'VC00006190': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 345
        },
        'VC00006540': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 311
        },
        'VC05200035352': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2228
        },
        'VC05200042875': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 1574
        },
        'VC05200060518': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2797
        },
        'VC00006417': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 574
        },
        'VC00006274': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 458
        },
        'VC05100010769': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 74,
            'edge_id': 2569
        },
        # Vineyard Vines
        'VC05200024971': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1312
        },
        'VC05200044678': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2422
        },
        'VC05200014711': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1030
        },
        'VC05200014672': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1027
        },
        'VC05200015014': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1002
        },
        'VC05200019949': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 697
        },
        'VC05200026104': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1325
        },
        'VC05200028181': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1190
        },
        'VC05200028187': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1319
        },
        'VC05200016679': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 854
        },
        'VC05200014956': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1069
        },
        'VC05200028266': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1417
        },
        'VC00006559': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 748
        },
        'VC00006482': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 308
        },
        'VC05200014736': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1031
        },
        'VC05200028145': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1323
        },
        'VC05200014816': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 876
        },
        'VC05200028229': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1326
        },
        'VC00004669': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 238
        },
        'VC05200009949': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 440
        },
        'VC05200014674': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1005
        },
        'VC05200015087': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 977
        },
        'VC05200014755': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 960
        },
        'VC00004212': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 393
        },
        'VC05100005715': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1767
        },
        'VC00006576': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 441
        },
        'VC05200028009': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1191
        },
        'VC05200013222': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 975
        },
        'VC05200028693': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1203
        },
        'VC05200009800': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 448
        },
        'VC05200070143': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 3106
        },
        'VC05200027111': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1385
        },
        'VC05200025569': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 922
        },
        'VC05200028647': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1322
        },
        'VC05200028140': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1300
        },
        'VC05200025425': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 971
        },
        'VC05200015164': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1083
        },
        'VC05100010989': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2384
        },
        'VC05200016763': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 978
        },
        'VC05200014799': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 961
        },
        'VC05200013998': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 963
        },
        'VC05200016702': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 974
        },
        'VC05200028193': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1316
        },
        'VC05200026746': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1087
        },
        'VC00006397': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 442
        },
        'VC05200015907': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 537
        },
        'VC05200063052': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2931
        },
        'VC05200026553': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1454
        },
        'VC05100021438': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2304
        },
        'VC05200014698': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 983
        },
        'VC00004677': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 237
        },
        'VC05100013251': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2116
        },
        'VC05200014807': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 872
        },
        'VC05200027779': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1184
        },
        'VC05200026356': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1324
        },
        'VC05200014706': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1358
        },
        'VC05200014666': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1379
        },
        'VC05200060291': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2837
        },
        'VC05200072719': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 443
        },
        'VC05200015092': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1032
        },
        'VC05200069399': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 3043
        },
        'VC05200015071': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 973
        },
        'VC05200028154': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1328
        },
        'VC05200015074': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1004
        },
        'VC05100021538': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2305
        },
        'VC05200014668': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1378
        },
        'VC05200029342': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1206
        },
        # Le Duff edges
        'VC05200036937': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2246
        },
        'VC05200038150': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2337
        },
        'VC05200046490': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2395
        },
        'VCE08400005273': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 3328
        },
        'VC05200057225': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1269
        },
        'VC05200027808': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1149
        },
        'VC05200039419': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2004
        },
        'VC05200026890': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1298
        },
        'VC05200056889': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2786
        },
        'VC05200036769': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1987
        },
        'VC05200037125': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1944
        },
        'VC05200037578': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2051
        },
        'VC05200046501': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2397
        },
        'VC05200014675': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 968
        },
        'VC05200014677': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 946
        },
        'VC05200038146': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2368
        },
        'VC05200036802': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2385
        },
        'VC05200014673': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1046
        },
        'VC05200039549': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2264
        },
        'VC05200039468': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2029
        },
        'VC05200038148': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2336
        },
        'VC05200036809': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1953
        },
        'VC05200056340': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2787
        },
        'VC05200058573': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2987
        },
        'VC05200058392': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2986
        },
        'VC05200055904': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2625
        },
        'VC05200028313': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1229
        },
        'VC05200032438': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1681
        },
        'VC05200014704': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 967
        },
        'VC05200036673': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1990
        },
        'VC05200014662': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1102
        },
        'VC05200015555': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 927
        },
        'VC05200058197': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2954
        },
        'VC05200036611': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1988
        },
        'VC05200028324': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1404
        },
        'VC05200036838': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2256
        },
        'VC05200028156': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1267
        },
        'VC05200014669': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 949
        },
        'VC05200037905': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2331
        },
        'VC05200057004': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2782
        },
        'VC05200015031': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 905
        },
        'VC05200027945': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1163
        },
        'VC05200037162': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1969
        },
        'VC05200032229': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1652
        },
        'VC05200036879': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2018
        },
        'VC05200037040': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2010
        },
        'VC05200028306': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1242
        },
        'VC05200037069': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1962
        },
        'VC05200045993': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2402
        },
        'VCE08400001519': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1479
        },
        'VC05200028224': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1293
        },
        'VC05200028226': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1227
        },
        'VC05200037797': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2359
        },
        'VC05200014856': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 943
        },
        'VC05200014712': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1070
        },
        'VC05200030905': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1733
        },
        'VC05200037557': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1964
        },
        'VC05200014717': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1106
        },
        'VC05200029318': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1380
        },
        'VC05200029570': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1476
        },
        'VC05200036804': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2028
        },
        'VC05200039053': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2255
        },
        'VC05200039216': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2174
        },
        'VC05200029921': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1439
        },
        'VC05200036795': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2016
        },
        'VC05200037179': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2009
        },
        'VC05200037626': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2361
        },
        'VC05200036880': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2017
        },
        'VC05200059018': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2993
        },
        'VC05200037192': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1968
        },
        'VC05200014932': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 3158
        },
        'VC05200037172': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2250
        },
        'VC05200028236': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1306
        },
        'VC05200016788': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 898
        },
        'VC05200037270': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1800
        },
        'VC05200030030': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1549
        },
        'VC05200036653': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1991
        },
        'VC05200028623': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1171
        },
        'VC05200016793': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 874
        },
        'VC05200014642': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 945
        },
        'VC05200028130': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1246
        },
        'VC05200046922': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2396
        },
        'VC05200037869': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2274
        },
        'VC05200028630': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1186
        },
        'VC05200028734': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1183
        },
        'VC05200015056': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1071
        },
        'VC05200027962': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1243
        },
        'VC05200036977': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2386
        },
        'VC05200033386': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1682
        },
        'VC05200028320': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1327
        },
        'VC05200038381': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2354
        },
        'VC05200051065': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2254
        },
        'VC05200026458': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1261
        },
        'VC05200014877': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1055
        },
        'VC05200026453': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1245
        },
        'VC05200029338': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1132
        },
        # 'VC05200028207': {
        #     'host': 'mettel.velocloud.net',
        #     'enterprise_id': 60,
        #     'edge_id': 1292
        # },
        'VC05200028206': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1212
        },
        'VC05200028204': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1295
        },
        'VC05200014739': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1050
        },
        'VC05200014633': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 948
        },
        'VC05200014984': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1131
        },
        'VC05200029335': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1176
        },
        'VC05200029231': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1466
        },
        'VC05200028725': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1193
        },
        'VC05200013228': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 847
        },
        'VC05200032600': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1951
        },
        'VC05200014888': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 901
        },
        'VC05200037872': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2363
        },
        'VC05200028844': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1521
        },
        'VC05200029909': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1204
        },
        'VC05200040328': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2266
        },
        'VC05200027977': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1162
        },
        'VC05200038729': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2027
        },
        'VC05200008657': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1822
        },
        'VC05200036959': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1989
        },
        'VC05200028192': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1291
        },
        'VC05200028214': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1313
        },
        'VC05200028216': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1305
        },
        'VC05200038286': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2356
        },
        'VC05200028211': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1260
        },
        'VC05200032479': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1662
        },
        'VC05200038671': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2921
        },
        'VC05200037322': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2030
        },
        'VC05200014622': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 944
        },
        'VC05200028440': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1650
        },
        'VC05200029736': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1537
        },
        'VC05200015357': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1079
        },
        'VC05200014744': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1078
        },
        'VC05200016781': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 994
        },
        'VC05200023238': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1381
        },
        'VC05200028589': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1440
        },
        'VC05200028991': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1185
        },
        'VC05200028180': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1294
        },
        'VC05200028612': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1192
        },
        'VC05200036749': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1963
        },
        'VC05200032226': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1683
        },
        'VC05200026261': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1247
        },
        'VC05200039524': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2005
        },
        'VC05200014618': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 750
        },
        'VC05200014757': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1146
        },
        'VC05200006854': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1399
        },
        'VC05200058820': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 3005
        },
        'VC05200015069': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1103
        },
        'VC05200014751': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1051
        },
        'VC05200014697': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1023
        },
        'VC05200030210': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1522
        },
        'VC05200014695': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1052
        },
        'VC05200015064': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1073
        },
        'VC05200028064': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1151
        },
        'VC05200016746': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 875
        },
        'VC05200015160': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1056
        },
        'VC05200037832': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2251
        },
        'VC05200015004': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 751
        },
        'VC05200016667': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 919
        },
        'VC05200036882': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1967
        },
        # 'VC05200015003': {
        #     'host': 'mettel.velocloud.net',
        #     'enterprise_id': 60,
        #     'edge_id': 1044
        # },
        'VC05200038421': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2257
        },
        'VC05200014886': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1076
        },
        'VC05200015070': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1075
        },
        'VC05200028277': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1272
        },
        'VC05200027244': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1211
        },
        'VC05200037109': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2387
        },
        'VC05200014602': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 962
        },
        'VC05200016017': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1129
        },
        'VC05200037201': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1798
        },
        'VC05200038870': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2357
        },
        'VC05200015606': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1045
        },
        'VC05200036817': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 2265
        },
        'VC05200022835': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1290
        },
        'VC05200028175': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1270
        },
        'VC05200034034': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1695
        },
        'VC05200028176': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1228
        },
        'VC05200032559': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1950
        },
        'VC05200030204': {
            'host': 'mettel.velocloud.net',
            'enterprise_id': 60,
            'edge_id': 1525
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

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
