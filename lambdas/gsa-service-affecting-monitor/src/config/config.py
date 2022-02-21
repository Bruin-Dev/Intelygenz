import logging
import os
import sys

from src.application import AffectingTroubles


CURRENT_ENVIRONMENT = os.environ['CURRENT_ENVIRONMENT']
ENVIRONMENT_NAME = os.environ['ENVIRONMENT_NAME']
TIMEZONE = os.environ['TIMEZONE']
VELOCLOUD_HOSTS = os.environ['MONITORED_VELOCLOUD_HOSTS'].split(',')

MONITOR_CONFIG = {
    'velo_filter': {
        host: [] for host in VELOCLOUD_HOSTS
    },
    'thresholds': {
        AffectingTroubles.LATENCY: int(os.environ['LATENCY_MONITORING_THRESHOLD']),          # milliseconds
        AffectingTroubles.PACKET_LOSS: int(os.environ['PACKET_LOSS_MONITORING_THRESHOLD']),  # packets
        AffectingTroubles.JITTER: int(os.environ['JITTER_MONITORING_THRESHOLD']),            # milliseconds
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
            os.environ['BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD']),  # percentage of total bandwidth
        AffectingTroubles.BOUNCING: int(
            os.environ['CIRCUIT_INSTABILITY_MONITORING_THRESHOLD']),         # number of down / dead events
    },
    'monitoring_minutes_per_trouble': {
        AffectingTroubles.LATENCY: int(os.environ['LATENCY_MONITORING_LOOKUP_INTERVAL']) // 60,
        AffectingTroubles.PACKET_LOSS: int(os.environ['PACKET_LOSS_MONITORING_LOOKUP_INTERVAL']) // 60,
        AffectingTroubles.JITTER: int(os.environ['JITTER_MONITORING_LOOKUP_INTERVAL']) // 60,
        AffectingTroubles.BANDWIDTH_OVER_UTILIZATION: int(
            os.environ['BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL']) // 60,
        AffectingTroubles.BOUNCING: int(os.environ['CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL']) // 60,
    },
    'blacklisted_edges': os.environ['BLACKLISTED_EDGES'].split(','),
}

LOG_CONFIG = {
    'name': 'gsa-service-affecting-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
}

EMAIL_CONFIG = {
    'account': os.environ['EMAIL_ACCOUNT'],
    'password': os.environ['EMAIL_PASSWORD'],
    'recipient': os.environ['EMAIL_RECIPIENT'],
}
