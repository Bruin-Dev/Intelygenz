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
        'outage_reporter': 60 * 240,
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
    # False positive in management status. Should be decomissioned.
    # 'VC05400014471': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 170,
    #     'edge_id': 2675
    # },
    'VCE08400000024': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 170,
        'edge_id': 1610
    },
    # Is an old edge but it's management status is Active.
    # 'VCE08400002428': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 170,
    #     'edge_id': 3195
    # },
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
    # Edge should be decomissioned
    # 'VC05400015370': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 170,
    #     'edge_id': 2674
    # },
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
    # Familia Health edges

    'VC05100050058': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 74,
        'edge_id': 2734
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
    # seems like a decomissioned edge
    # 'VC05200050962': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 74,
    #     'edge_id': 2535
    # },
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
    # Cannot get management status but should be active
    # 'VC05200009868': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 74,
    #     'edge_id': 469
    # },
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

    # Le Duff edges
    'VC05200036937': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2246
    },
    'VC05200046490': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2395
    },

    # Management status not found.
    # 'VCE08400005273': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 3328
    # },
    #    'VC05200027808': {
    #        'host': 'mettel.velocloud.net',
    #        'enterprise_id': 120,
    #        'edge_id': 1149
    #    },
    'VC05200039419': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2004
    },
    'VC05200026890': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1298
    },
    'VC05200056889': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2786
    },
    'VC05200036769': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1987
    },
    'VC05200037125': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1944
    },
    'VC05200037578': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2051
    },
    'VC05200046501': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2397
    },
    'VC05200036802': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2385
    },
    # 'VC05200014673': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1046
    # },
    'VC05200039549': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2264
    },
    'VC05200039468': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2029
    },
    # Inactive for two weeks. No management status
    # 'VC05200038148': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 2336
    # },
    'VC05200036809': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1953
    },
    'VC05200056340': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2787
    },
    'VC05200058573': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2987
    },
    'VC05200058392': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2986
    },
    # Error in Bruin. Should be active
    # 'VC05200028313': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1229
    # },
    'VC05200032438': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1681
    },
    'VC05200036673': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1990
    },
    # Management status not found
    # 'VC05200014662': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1102
    # },
    #    'VC05200015555': {
    #        'host': 'mettel.velocloud.net',
    #        'enterprise_id': 120,
    #        'edge_id': 927
    #    },
    'VC05200058197': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2954
    },
    'VC05200036611': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1988
    },
    'VC05200036838': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2256
    },
    # Seems like and old one
    # 'VC05200028156': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1267
    # },
    # 'VC05200014669': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 949
    # },
    'VC05200037905': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2331
    },
    'VC05200057004': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2782
    },
    #    'VC05200015031': {
    #        'host': 'mettel.velocloud.net',
    #        'enterprise_id': 120,
    #        'edge_id': 905
    #    },
    # 'VC05200027945': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1163
    # },
    'VC05200037162': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1969
    },
    'VC05200032229': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1652
    },
    'VC05200036879': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2018
    },
    'VC05200037040': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2010
    },
    'VC05200037069': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1962
    },
    'VC05200045993': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2402
    },
    'VCE08400001519': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1479
    },
    'VC05200028224': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1293
    },
    'VC05200037797': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2359
    },
    #    'VC05200014856': {
    #        'host': 'mettel.velocloud.net',
    #        'enterprise_id': 120,
    #        'edge_id': 943
    #    },
    # 'VC05200014712': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1070
    # },
    'VC05200030905': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1733
    },
    'VC05200037557': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1964
    },
    # 'VC05200014717': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1106
    # },
    'VC05200029318': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1380
    },
    'VC05200029570': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1476
    },
    'VC05200036804': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2028
    },
    'VC05200039053': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2255
    },
    'VC05200039216': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2174
    },
    'VC05200029921': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1439
    },
    'VC05200036795': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2016
    },
    'VC05200037179': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2009
    },
    'VC05200036880': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2017
    },
    'VC05200059018': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2993
    },
    'VC05200037192': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1968
    },
    # Test edge leftover
    # 'VC05200014932': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 3158
    # },
    'VC05200037172': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2250
    },
    'VC05200028236': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1306
    },
    'VC05200037270': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1800
    },
    'VC05200030030': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1549
    },
    'VC05200036653': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1991
    },

    'VC05200014642': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 945
    },
    'VC05200028130': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1246
    },
    'VC05200046922': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2396
    },
    'VC05200037869': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2274
    },
    # 'VC05200028734': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1183
    # },
    # 'VC05200015056': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1071
    # },
    'VC05200036977': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2386
    },
    'VC05200033386': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1682
    },
    'VC05200028320': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1327
    },
    'VC05200051065': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2254
    },
    # 'VC05200014877': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1055
    # },
    'VC05200026453': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1245
    },
    'VC05200028207': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1292
    },
    # Management status wrong in Bruin
    # 'VC05200028206': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1212
    # },
    'VC05200028204': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1295
    },
    # 'VC05200014739': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1050
    # },
    # 'VC05200014633': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 948
    # },
    # 'VC05200014984': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1131
    # },
    # 'VC05200029335': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1176
    # },
    # 'VC05200029909': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1204
    # },

    'VC05200038729': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2027
    },
    # Inactive when added
    # 'VC05200036959': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1989
    # },
    'VC05200028192': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1291
    },
    'VC05200028216': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1305
    },
    'VC05200038671': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2921
    },
    'VC05200037322': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2030
    },
    # Marked as old in velo.
    # 'VC05200014622': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 944
    # },
    'VC05200028440': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1650
    },

    # No management status found
    # 'VC05200015357': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1079
    # },
    # No management status found
    # 'VC05200014744': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1078
    # },
    'VC05200016781': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 994
    },
    'VC05200023238': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1381
    },
    'VC05200028589': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1440
    },
    # Inactive for two weeks when added. No management status
    # 'VC05200028991': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1185
    # },
    'VC05200028180': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1294
    },
    'VC05200036749': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1963
    },
    'VC05200032226': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1683
    },
    # Old device not removed from velo
    # 'VC05200026261': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1247
    # },
    # Marked as decomissioned in velocloud
    # 'VC05200039524': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 2005
    # },
    'VC05200014618': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 750
    },
    # 'VC05200014757': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1146
    # },
    # Test edge leftover
    # 'VC05200006854': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1399
    # },
    'VC05200058820': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 3005
    },
    # Management status not found
    # 'VC05200015069': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1103
    # },
    # 'VC05200014751': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1051
    # },
    # 'VC05200014695': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1052
    # },
    # 'VC05200015064': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1073
    # },
    # 'VC05200015160': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1056
    # },
    'VC05200037832': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2251
    },
    #    'VC05200015004': {
    #        'host': 'mettel.velocloud.net',
    #        'enterprise_id': 120,
    #        'edge_id': 751
    #    },
    'VC05200036882': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1967
    },
    'VC05200015003': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1044
    },
    'VC05200038421': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2257
    },
    # Management status not found
    # 'VC05200014886': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1076
    # },
    'VC05200037109': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2387
    },
    # 'VC05200014602': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 962
    # },
    # 'VC05200016017': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1129
    # },
    'VC05200037201': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1798
    },
    # 'VC05200015606': {
    #     'host': 'mettel.velocloud.net',
    #     'enterprise_id': 120,
    #     'edge_id': 1045
    # },
    'VC05200036817': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 2265
    },
    'VC05200022835': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1290
    },
    'VC05200034034': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1695
    },
    'VC05200032559': {
        'host': 'mettel.velocloud.net',
        'enterprise_id': 120,
        'edge_id': 1950
    },

}
