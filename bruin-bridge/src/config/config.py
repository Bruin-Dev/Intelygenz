# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source .env in this directory.
# If you dont have any .env files, ask for one they are not in VCS
import os

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'cluster_name': os.environ["NATS_CLUSTER_NAME"],
    'client_ID': 'bruin-bridge',
    'consumer': {
        'start_at': 'first',
        'topic': 'Some-topic'
    }
}