# You must replicate the structure of config.py, changing os.environ calls for mock values

NATS_CONFIG = {
    'servers': 'nats://nats-streaming:4222',
    'cluster_name': 'automation-engine-nats',
    'client_ID': 'bruin-bridge',
    'consumer': {
        'start_at': 'first',
        'topic': 'Some-topic'
    }
}
