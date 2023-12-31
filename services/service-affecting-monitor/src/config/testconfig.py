# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

from application import AffectingTroubles

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
    "multiplier": 1,
    "min": 1,
    "stop_delay": 0,
}

TIMEZONE = "US/Eastern"

IPA_SYSTEM_USERNAME_IN_BRUIN = "Intelygenz Ai"

PRODUCT_CATEGORY = "SD-WAN"

VELOCLOUD_HOST = "test-host"

UMBRELLA_HOSTS = {
    "host-2": "Client 3",
    "host-3": "Client 4",
}

MONITOR_CONFIG = {
    "contact_info_by_host_and_client_id": {
        "host-1": {
            1: [
                {
                    "email": "test@client1.com",
                    "name": "Client 1",
                    "type": "ticket",
                },
                {
                    "email": "test@client1.com",
                    "name": "Client 1",
                    "type": "site",
                },
            ],
            2: [
                {
                    "email": "test@client2.com",
                    "name": "Client 2",
                    "type": "ticket",
                },
                {
                    "email": "test@client2.com",
                    "name": "Client 2",
                    "type": "site",
                },
            ],
        },
        "host-2": {
            "*": [
                {
                    "email": "test@client3.com",
                    "name": "Client 3",
                    "type": "ticket",
                },
                {
                    "email": "test@client3.com",
                    "name": "Client 3",
                    "type": "site",
                },
            ]
        },
        "host-3": {
            "*": [
                {
                    "email": "test@client4.com",
                    "name": "Client 4",
                    "type": "ticket",
                },
                {
                    "email": "test@client4.com",
                    "name": "Client 4",
                    "type": "site",
                },
            ]
        },
    },
    "customers_to_always_use_default_contact_info": [1],
    "velo_filter": {
        "test-host": [],
    },
    "monitoring_minutes_interval": 10,
    "thresholds": {
        AffectingTroubles.LATENCY: 140,  # milliseconds
        AffectingTroubles.PACKET_LOSS: 8,  # packets
        AffectingTroubles.JITTER: 50,  # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 90,  # percentage of total bandwidth
        AffectingTroubles.BOUNCING: 10,  # number of down / dead events
    },
    "wireless_thresholds": {
        AffectingTroubles.LATENCY: 140,  # milliseconds
        AffectingTroubles.PACKET_LOSS: 10,  # packets
        AffectingTroubles.JITTER: 50,  # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 90,  # percentage of total bandwidth
        AffectingTroubles.BOUNCING: 10,  # number of down / dead events
    },
    "monitoring_minutes_per_trouble": {
        AffectingTroubles.LATENCY: 30,
        AffectingTroubles.PACKET_LOSS: 30,
        AffectingTroubles.JITTER: 30,
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 30,
        AffectingTroubles.BOUNCING: 60,
    },
    "wireless_monitoring_minutes_per_trouble": {
        AffectingTroubles.LATENCY: 90,
        AffectingTroubles.PACKET_LOSS: 90,
        AffectingTroubles.JITTER: 90,
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 90,
        AffectingTroubles.BOUNCING: 60,
    },
    "blacklisted_link_labels_for_asr_forwards": ["byob"],
    "blacklisted_link_labels_for_hnoc_forwards": ["byob"],
    "autoresolve": {
        "semaphore": 3,
        "metrics_lookup_interval_minutes": 30,
        "day_schedule": {"start_hour": 8, "end_hour": 0},
        "last_affecting_trouble_seconds": {"day": 1.5 * 60 * 60, "night": 3 * 60 * 60},
        "max_autoresolves": 3,
        "thresholds": {
            AffectingTroubles.BOUNCING: 4,
        },
    },
    "customers_with_bandwidth_enabled": [1, 2, 3],
    "customers_with_bandwidth_disabled": [6, 7, 8],
    "wait_time_before_sending_new_milestone_reminder": 86400,
}

MONITOR_REPORT_CONFIG = {
    "exec_on_start": False,
    "environment": "test",
    "semaphore": 5,
    "wait_fixed": 1,
    "stop_after_attempt": 2,
    "crontab": "0 8 * * *",
    "threshold": 3,
    "active_reports": ["Jitter", "Latency", "Packet Loss", "Bandwidth Over Utilization"],
    "trailing_days": 14,
    "default_contacts": ["mettel.automation@intelygenz.com"],
    "recipients_by_host_and_client_id": {
        "test-host": {
            9994: ["HNOCleaderteam@mettel.net"],
        },
    },
}

BANDWIDTH_REPORT_CONFIG = {
    "exec_on_start": False,
    "environment": "test",
    "timezone": "US/Eastern",
    "crontab": "0 8 * * *",
    "lookup_interval_hours": 24,
    "default_contacts": ["mettel.automation@intelygenz.com"],
    "recipients_by_host_and_client_id": {
        "test-host": {
            9994: ["HNOCleaderteam@mettel.net"],
        },
    },
}

CURRENT_ENVIRONMENT = "dev"
ENVIRONMENT_NAME = "dev"

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

QUART_CONFIG = {"title": "service-affecting-monitor", "port": 5000}

METRICS_SERVER_CONFIG = {"port": 9090}
