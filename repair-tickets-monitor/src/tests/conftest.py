from unittest.mock import Mock
import pytest

from application.server.api_server import APIServer
from application.repositories.storage_repository import StorageRepository
from config import testconfig as config


# Scopes
# - function
# - module
# - session


@pytest.fixture(scope='function')
def logger():
    return Mock()


@pytest.fixture(scope='function')
def redis():
    return Mock()


@pytest.fixture(scope='function')
def bruin_repository():
    return Mock()


@pytest.fixture(scope='function')
def repair_tickets_repository():
    return Mock()


@pytest.fixture(scope='function')
def repair_tickets_kre_repository():
    return Mock()


@pytest.fixture(scope='function')
def notifications_repository():
    return Mock()


@pytest.fixture(scope='function')
def utils_repository():
    return Mock()


@pytest.fixture(scope='function')
def storage_repository(logger, redis):
    return StorageRepository(config, logger, redis)


@pytest.fixture(scope='function')
def prediction_response_voo(logger, redis):
    return {
        'status': 200,
        'body': {
            'above_threshold': True,
            'in_validation_set': False,
            'service_numbers': [
                '2109677750'
            ],
            'prediction_class': 'VOO'
        }
    }


@pytest.fixture(scope='function')
def prediction_response_vas(logger, redis):
    return {
        'status': 200,
        'body': {
            'above_threshold': True,
            'in_validation_set': False,
            'service_numbers': [
                '2109677751'
            ],
            'prediction_class': 'VAS'
        }
    }


@pytest.fixture(scope='function')
def prediction_response_others(logger, redis):
    return {
        'status': 200,
        'body': {
            'above_threshold': True,
            'in_validation_set': False,
            'service_numbers': [
                '2109677752'
            ],
            'prediction_class': 'OTHER'
        }
    }


@pytest.fixture(scope='function')
def create_voo_ticket_response(logger, redis):
    return {
        'status': 200,
        'body': {
            "clientId": 0,
            "wtNs": [
                "string"
            ],
            "referenceTicketNumber": "string",
            "requestDescription": "string",
            "localContact": {
                "name": "string",
                "phone": "string",
                "email": "string"
            }
        }
    }
