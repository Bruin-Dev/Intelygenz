# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

from application import AffectingTroubles

NATS_CONFIG = {
    "servers": "nats://nats-server:4222",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

VELOCLOUD_HOST = "some-host"

PRODUCT_CATEGORY = "SD-WAN"

IPA_SYSTEM_USERNAME_IN_BRUIN = "Intelygenz Ai"

UMBRELLA_HOSTS = {}

MONITOR_CONFIG = {
    "monitoring_interval_seconds": 60 * 5,
    "blacklisted_edges": [{"host": "some-host", "enterprise_id": 1, "edge_id": 1}],
    "semaphore": 10,
    "velo_filter": {
        VELOCLOUD_HOST: [],
    },
    "tnba_notes_age_for_new_appends_in_minutes": 30,
    "last_outage_seconds": 60 * 60,
    "request_repair_completed_confidence_threshold": 0.75,
    "service_affecting": {
        "metrics_lookup_interval_minutes": 10,
        "thresholds": {
            AffectingTroubles.LATENCY: 140,  # milliseconds
            AffectingTroubles.PACKET_LOSS: 8,  # packets
            AffectingTroubles.JITTER: 50,  # milliseconds
            AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: 90,  # percentage of total bandwidth
            AffectingTroubles.BOUNCING: 4,  # number of down / dead events
        },
        "monitoring_minutes_per_trouble": {
            AffectingTroubles.BOUNCING: 60,
        },
    },
}

CURRENT_ENVIRONMENT = "dev"

ENVIRONMENT_NAME = "dev"

TIMEZONE = "US/Eastern"

LOG_CONFIG = {
    "name": "test-name",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}

QUART_CONFIG = {"title": "tnba-monitor", "port": 5000}

METRICS_SERVER_CONFIG = {"port": 9090}
