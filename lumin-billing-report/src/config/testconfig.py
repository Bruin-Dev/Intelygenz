# You must replicate the structure of config.py, changing os.environ calls for mock values
import os
import logging
import sys

LUMIN_CONFIG = {
    'uri': 'https://foo.bar',
    'token': 'foobarbaz',
    'multiplier': 1,
    'min': 0.1,
    'stop_delay': 0.1
}

BILLING_REPORT_CONFIG = {
    'customer_name': 'foo',
    'recipient': "some.recipient@email.com",
    'timezone': 'US/Eastern',
    'date_format': '%m/%d/%Y',
    'fieldnames': [
        'id',
        'conversation_id',
        'type',
        'host_id',
        'host_did',
        'user_did',
        'timestamp',
        'fake'
    ]
}

EMAIL_CONFIG = {
    'sender_email': 'fake@gmail.com',
    'password': '456',
    'recipient_email': 'fake@gmail.com'
}

LOG_CONFIG = {
    'name': 'billing-automation',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '%(asctime)s: %(module)s: %(levelname)s: %(message)s'
}

QUART_CONFIG = {
    'title': 'billing-automation',
    'port': 5000
}
