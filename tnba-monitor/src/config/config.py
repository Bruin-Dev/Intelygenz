# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'subscriber': {
        'pending_limits': 65536
    },
    'multiplier': 5,
    'min': 5,
    'stop_delay': 300,
    'reconnects': 150
}

MONITOR_CONFIG = {
    'refresh_map_time': 60 * 4,
    'blacklisted_edges': [
        # Federal edge that is inside a non-federal Velocloud instance
        {'host': 'mettel.velocloud.net', 'enterprise_id': 170, 'edge_id': 3195}
    ],
    'semaphore': 1,
    'velo_filter': {"mettel.velocloud.net": [],
                    "metvco02.mettel.net": [],
                    "metvco03.mettel.net": [],
                    "metvco04.mettel.net": []},
    'tnba_notes_age_for_new_appends_in_minutes': 30,
    'last_outage_seconds': 60 * 60,
    'request_repair_completed_confidence_threshold': 0.75,
}

ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]

TIMEZONE = 'US/Eastern'

MONITORING_INTERVAL_SECONDS = 60 * 5

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

LOG_CONFIG = {
    'name': 'tnba-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-tnba-monitor'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'tnba-monitor',
    'port': 5000
}

CONDITIONS = {
    "ticket_min_age_minutes": 45,
    "automatable_task_list": ["Repair Completed",
                              "Request Completed",
                              "Holmdel NOC Investigate",
                              "No Trouble Found - Carrier Issue",
                              "Refer to Holmdel NOC for Repair",
                              "Wireless Repair Intervention Needed"],
    "max_recursive_depth": 7,
    "min_probability_threshold": 0.60
}

TRANSITION_MAP = {
    "None": ["Holmdel NOC Investigate ", "Wireless Repair Intervention Needed", "Repair Completed",
             "Request Completed"],
    "Holmdel NOC Investigate ": ["Wireless Repair Intervention Needed", "Repair Completed", "Request Completed"]
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
