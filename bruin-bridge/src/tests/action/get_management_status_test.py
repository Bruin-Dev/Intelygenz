import json
from unittest.mock import Mock

import pytest
from application.actions.get_management_status import GetManagementStatus
from asynctest import CoroutineMock


class TestGetManagementStatus:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)

        assert get_management_status._logger is logger
        assert get_management_status._event_bus is event_bus
        assert get_management_status._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_management_status_ok_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = [
            {
                "clientID": 9994,
                "clientName": "METTEL/NEW YORK",
                "vendor": "MetTel",
                "serviceNumber": "VC05400009999",
                "siteId": 2048,
                "siteLabel": "MetTel Network Services",
                "address": {
                    "address": "Fake street",
                    "city": "Fake city",
                    "state": "Fake state",
                    "zip": "9999",
                    "country": "Fake Country"
                },
                "description": None,
                "installDate": "2019-08-21T05:00:00Z",
                "disconnectDate": None,
                "status": "A",
                "verified": "Y",
                "productCategory": "SD-WAN",
                "productType": "SD-WAN",
                "items": [
                    {
                        "itemName": "Licensed Software - SD-WAN 100M",
                        "primaryIndicator": "SD-WAN"
                    }
                ],
                "contractIdentifier": "0",
                "rateCardIdentifier": None,
                "lastInvoiceUsageDate": None,
                "lastUsageDate": None,
                "longitude": -74.009781,
                "latitude": 40.7035351
            }
        ]
        bruin_repository.get_management_status = Mock(return_value=management_status)

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999"
        }

        event_bus_request = {
            "request_id": 19,
            "filters": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'management_status': management_status,
            'status': 200
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_called_once_with(filters)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_management_status_no_client_id_ko_test(self):
        logger = Mock()
        logger.error = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = None

        filters = {}

        event_bus_request = {
            "request_id": 19,
            "filters": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            "management_status": management_status,
            "error_message": "You must specify client_id in the filter",
            "status": 400
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_not_called()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called

    @pytest.mark.asyncio
    async def get_management_status_no_management_status_ko_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        management_status = None
        bruin_repository.get_management_status = Mock(return_value=management_status)

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999"
        }

        event_bus_request = {
            "request_id": 19,
            "filters": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'management_status': management_status,
            'status': 500
        }

        get_management_status = GetManagementStatus(logger, event_bus, bruin_repository)
        await get_management_status.get_management_status(event_bus_request)
        bruin_repository.get_management_status.assert_called_once_with(filters)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called
