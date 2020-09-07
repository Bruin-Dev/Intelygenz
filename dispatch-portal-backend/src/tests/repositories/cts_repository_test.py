from unittest.mock import Mock

from application.repositories import cts_repository as update_body_with_client_address

from config import testconfig
from application.repositories.cts_repository import CtsRepository


class TestCtsRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        cts_repository = CtsRepository(logger, config, event_bus, notifications_repository)

        assert cts_repository._event_bus is event_bus
        assert cts_repository._logger is logger
        assert cts_repository._config is config
        assert cts_repository._notifications_repository is notifications_repository

    def update_body_with_client_address(self):
        body = {
            'clientName': 'Red Rose Inn',
            'address': {'address': '123 Fake Street', 'city': 'Pleasantown', 'state': 'CA', 'zip': '99088',
                        'country': 'United States'}
        }

        response_expected = {'job_site': 'Red Rose Inn',
                             'job_site_street_1': '123 Fake Street',
                             'job_site_city': 'Pleasantown',
                             'job_site_state': 'CA',
                             'job_site_zip_code': '99088',
                             'location_country': 'United States'
                             }
        response_body = update_body_with_client_address(body)
        assert response_body == response_expected
