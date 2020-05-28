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

DISPATCH_MONITOR_CONFIG = {
    'environment': os.environ["CURRENT_ENVIRONMENT"],
    'timezone': 'US/Eastern',
    'jobs_intervals': {
        'dispatch_monitor': 60 * 15
    },
    'confirmed_semaphore': 5,
    'tech_on_site_semaphore': 5,
    'dispatches_completed_semaphore': 5,
}

LOG_CONFIG = {
    'name': 'service-dispatch-monitor',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s - %(funcName)20s: %(message)s'
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
