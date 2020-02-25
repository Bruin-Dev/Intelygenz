# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys
from config.customer_list import customer_list as CUSTOMER_LIST

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

TIMEZONE = 'US/Eastern'

MONITORING_INTERVAL_SECONDS = 60 * 10

LOG_CONFIG = {
    'name': 'tnba-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'tnba-monitor',
    'port': 5000
}

GRAFANA_CONFIG = {
    'port': 9090
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
    "None": ["Holmdel NOC Investigate ", "Wireless Repair Intervention Needed"],
    "Holmdel NOC Investigate ": ["Wireless Repair Intervention Needed"]
}

CUSTOMER_LIST = CUSTOMER_LIST

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
