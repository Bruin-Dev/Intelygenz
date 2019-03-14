# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os

NATS_CONFIG = {
    'servers': [os.environ["NATS_SERVER1"]],
    'cluster_name': os.environ["NATS_CLUSTER_NAME"],
    'publisher': {
        'max_pub_acks_inflight': 1
    }
}


def parse_velocloud_config():
    credential_blocks = os.environ["VELOCLOUD_CREDENTIALS"].split(";")
    credential_blocks_splitted = [credential_block.split("+") for credential_block in credential_blocks]
    return [
        {'url': cred_block[0],
         'username': cred_block[1],
         'password': cred_block[2]
         }
        for cred_block in credential_blocks_splitted]


VELOCLOUD_CONFIG = {
    'verify_ssl': os.environ["VELOCLOUD_VERIFY_SSL"],
    'servers': parse_velocloud_config()
}

OVERSEER_CONFIG = {
    'interval_time': 600
}

LOG_CONFIG = {
    'name': 'velocloud-overseer-log',
}
