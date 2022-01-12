# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys
import json


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

ENVIRONMENT_NAME = os.getenv('ENVIRONMENT_NAME')

INTERMAPPER_CONFIG = {
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    'monitoring_interval': 30,
    'inbox_email': 'mettel.automation@intelygenz.com',
    'sender_emails_list': ['noreply@mettel.net'],
    'concurrent_email_batches': 10,
    'intermapper_down_events': ['Down', 'Critical', 'Alarm', 'Warning', 'Link Warning'],
    'intermapper_up_events': ['Up', 'OK'],
    'autoresolve_last_outage_seconds': 60 * 75,
    'autoresolve_product_category_list': ['Cloud Connect', 'Cloud Firewall', 'POTS in a Box', 'Premise Firewall',
                                          'Routers', 'SIP Trunking', 'Switches', 'VPNS', 'Wi-Fi', 'SD-WAN'],
    'dri_parameters': [
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
        "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress"
    ],
    'stop_after_attempt': 5,
    'wait_multiplier': 1,
    'wait_min': 4,
    'wait_max': 10

}
LOG_CONFIG = {
    'name': 'intermapper-outage-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-intermapper-outage-monitor'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'intermapper-outage-monitor',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
