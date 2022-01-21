# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys
import os

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'subscriber': {
        'pending_limits': 65536
    },
    'publisher': {
        'max_pub_acks_inflight': 6000
    }
}

LOG_CONFIG = {
    'name': 'test-name',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'intermapper-outage-monitor',
    'port': 5000
}

ENVIRONMENT_NAME = "dev"

INTERMAPPER_CONFIG = {
    'environment': ENVIRONMENT_NAME,
    'timezone': 'US/Eastern',
    'monitoring_interval': 30,
    'inbox_email': 'fake@gmail.com',
    'sender_emails_list': ['fakesender@email.com'],
    'concurrent_email_batches': 10,
    'intermapper_down_events': ['Down', 'Critical', 'Alarm', 'Warning', 'Link Warning'],
    'intermapper_up_events': ['Up', 'OK'],
    'autoresolve_last_outage_seconds': 60 * 60,
    'autoresolve_product_category_list': ['Cloud Connect', 'Cloud Firewall', 'POTS in a Box', 'Premise Firewall',
                                          'Routers', 'SIP Trunking', 'Switches', 'VPNS', 'Wi-Fi'],
    'dri_parameters': [
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
        "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress"
    ],
    'stop_after_attempt': 0,
    'wait_multiplier': 0,
    'wait_min': 0,
    'wait_max': 0

}
