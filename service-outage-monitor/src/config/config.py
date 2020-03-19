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
    'velocloud_instances_filter': {
        "mettel.velocloud.net": [],
    },
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
        # False positive in management status. Should be decomissioned: 'VC05400014471' 'VC05400015370'
        'VC05400017787', 'VC05400018334', 'VC05200039042', 'VC05400018645', 'VC05200039063', 'VC05200043037',
        'VC05400006773', 'VCE08400002713', 'VC05200056383', 'VC05200069615', 'VC05400012544',
        'VCE08400000024', 'VCE08400003079', 'VC05100042088', 'VC05200035353', 'VCE08400000896',
        'VCE08400000737', 'VC05200044788', 'VCE08400002115', 'VC05400010813', 'VCE08400002682', 'VC05200043272',
        'VC05200062803', 'VC05400011928', 'VC05400014486', 'VC05200043505', 'VC05200038567', 'VC05400012064',
        'VC05400023946', 'VCE08400002673', 'VC05400015426', 'VC05400014293', 'VCE08400001089',
        'VC05400015392', 'VC05200045071', 'VC05400011799', 'VCE08400004143', 'VC05400006582', 'VC05400017307',
        'VC05200038305',
        # Familia health
        'VC05100050058', 'VC05200044799', 'VCE08400005358', 'VC05200030750', 'VC05200013093', 'VC05100050542',
        'VC05100037867', 'VC05100005736', 'VC00006387', 'VC05100050636', 'VC05200035420', 'VC05200025712',
        'VC05200025858', 'VC00006483', 'VC05200025993', 'VC00006487', 'VC00006677', 'VC05200025718', 'VC05100010741',
        'VC05100005777', 'VC05100050256', 'VC05200027330', 'VC05200029438', 'VC05200056131', 'VC05200058778',
        'VC05100009902', 'VC05100015061', 'VC05200038404', 'VC05200025788', 'VC05100049912', 'VC05200024848',
        'VC05100020484', 'VC05100011001', 'VC05200012003', 'VC05200025522', 'VC05200011116', 'VC05100024269',
        'VC05100041018', 'VC05200027081', 'VC05200026330', 'VC05100026734', 'VC05200008978', 'VC05200025705',
        'VC00006495', 'VC05100042279', 'VC05200014645', 'VC05100010740', 'VC05200045072', 'VC05200029048',
        'VC05200009111', 'VC00006373', 'VC05100042887', 'VC00006190', 'VC00006540', 'VC05200035352', 'VC05200042875',
        'VC05200060518', 'VC00006417', 'VC00006274', 'VC05100010769'
    ],
    'autoresolve_down_events_seconds': 45 * 60,
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

TRIAGE_CONFIG = {
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'polling_minutes': 10,
    'recipient': os.environ["LAST_CONTACT_RECIPIENT"],
    'timezone': 'US/Eastern',
    'monitoring_seconds': 120,
    'event_limit': 15,
    'velo_filter': {},
}
