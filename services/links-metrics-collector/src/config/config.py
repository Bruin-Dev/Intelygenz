# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os
import logging
import sys

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
CURRENT_ENVIRONMENT = os.getenv('CURRENT_ENVIRONMENT')

SCHEDULER_TIMEZONE = 'US/Eastern'
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASS = os.getenv('MONGO_PASS')
MONGO_URL = os.getenv('MONGO_URL')
MONGO_PORT = os.getenv('MONGO_PORT')
STORING_INTERVAL_MINUTES = 15
VELO_HOST = "mettel.velocloud.net"
OREILLY_CLIENT_ID = 22
METRICS_LIST = ['bytesRx', 'bytesTx', 'totalBytes', 'totalPackets', 'p1BytesRx', 'p1BytesTx', 'p1PacketsRx',
                'p1PacketsTx', 'p2BytesRx', 'p2BytesTx', 'p2PacketsRx', 'p2PacketsTx', 'p3BytesRx', 'p3BytesTx',
                'p3PacketsRx', 'p3PacketsTx', 'packetsRx', 'packetsTx', 'controlBytesRx', 'controlBytesTx',
                'controlPacketsRx', 'controlPacketsTx', 'bestJitterMsRx', 'bestJitterMsTx', 'bestLatencyMsRx',
                'bestLatencyMsTx', 'bestLossPctRx', 'bestLossPctTx', 'bpsOfBestPathRx', 'bpsOfBestPathTx',
                'signalStrength', 'scoreTx', 'scoreRx']

LOG_CONFIG = {
    'name': 'links-metrics-collector',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': f'%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s',
    'papertrail': {
        'active': True if os.getenv('PAPERTRAIL_ACTIVE') == "true" else False,
        'prefix': os.getenv('PAPERTRAIL_PREFIX', f'{ENVIRONMENT_NAME}-links-metrics-collector'),
        'host': os.getenv('PAPERTRAIL_HOST'),
        'port': int(os.getenv('PAPERTRAIL_PORT'))
    },
}

QUART_CONFIG = {
    'title': 'links-metrics-collector',
    'port': 5000
}

REDIS = {
    "host": os.environ["REDIS_HOSTNAME"]
}
