from enum import Enum

nats_error_response = {'body': None, 'status': 503}


class Outages(Enum):
    NODE_TO_NODE = 'Node to Node'
    REAL_SERVICE = 'Real Service'
