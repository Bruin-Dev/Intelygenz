# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
import sys

NATS_CONFIG = {
    'servers': 'nats://nats-server:4222',
    'client_ID': 'digi-reboot-report-test',
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

TIMEZONE = 'US/Eastern'

DIGI_CONFIG = {
    'days_of_digi_recovery_log': 2,
    'digi_reboot_report_time': 60 * 24,
    'recipient': "some.recipient@email.com",
}

CURRENT_ENVIRONMENT = 'dev'
ENVIRONMENT_NAME = 'dev'

QUART_CONFIG = {
    'title': 'digi-reboot-report',
    'port': 5000
}

METRICS_SERVER_CONFIG = {
    'port': 9090
}
