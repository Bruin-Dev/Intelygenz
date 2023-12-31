# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import os
import sys

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

QUART_CONFIG = {"title": "intermapper-outage-monitor", "port": 5000}

CURRENT_ENVIRONMENT = "dev"
ENVIRONMENT_NAME = "dev"

TIMEZONE = "US/Eastern"

INTERMAPPER_CONFIG = {
    "monitoring_interval": 30,
    "inbox_email": "fake@gmail.com",
    "observed_emails_list": [],
    "sender_emails_list": ["fakesender@email.com"],
    "concurrent_email_batches": 10,
    "max_emails_to_retrieve": 100,
    "intermapper_down_events": ["Down", "Critical", "Alarm", "Warning", "Link Warning"],
    "intermapper_up_events": ["Up", "OK"],
    "autoresolve": {
        "day_schedule": {"start_hour": 8, "end_hour": 0},
        "last_outage_seconds": {"day": 1.5 * 60 * 60, "night": 3 * 60 * 60},
        "max_autoresolves": 3,
        "product_category_list": [
            "Cloud Connect",
            "Cloud Firewall",
            "POTS in a Box",
            "Premise Firewall",
            "Routers",
            "SIP Trunking",
            "Switches",
            "VPNS",
            "Wi-Fi",
        ],
    },
    "dri_parameters": [
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
        "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
    ],
    "events_lookup_days": 1,
    "stop_after_attempt": 0,
    "wait_multiplier": 0,
    "wait_min": 0,
    "wait_max": 0,
    "battery_alert_probe_types": ["Data Remote Probe"],
    "battery_alert_probe_conditions": ["Device Lost Power - Battery is in use"],
    "forward_to_hnoc_job_interval": 30,
    "forward_to_ipa_job_interval": 60,
    "monitor_piab_devices": True,
}

METRICS_SERVER_CONFIG = {"port": 9090}
