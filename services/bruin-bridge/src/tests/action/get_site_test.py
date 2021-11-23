from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock

from application.actions.get_site import GetSite


class TestGetSite:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        get_site = GetSite(logger, event_bus, bruin_repository)

        assert get_site._logger is logger
        assert get_site._event_bus is event_bus
        assert get_site._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_site_ok_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        client_id = 72959
        site_id = 343443
        params = {
            "client_id": client_id,
            "site_id": site_id
        }
        get_site_response = {
            "body": {
                "client_id": client_id,
                "site_id": site_id
            },
            "status": 200
        }
        bruin_repository.get_site = CoroutineMock(return_value=get_site_response)

        event_bus_request = {
            "request_id": 19,
            "body": params,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            **get_site_response,
        }

        get_site = GetSite(logger, event_bus, bruin_repository)
        await get_site.get_site(event_bus_request)
        bruin_repository.get_site.assert_awaited_once_with(params)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.info.called

    @pytest.mark.asyncio
    async def get_site_no_filters_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_site = CoroutineMock()

        event_bus_request = {
            "request_id": 19,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify '
                    '{.."body":{"client_id":...}} in the request',
            'status': 400
        }

        get_site = GetSite(logger, event_bus, bruin_repository)
        await get_site.get_site(event_bus_request)
        bruin_repository.get_site.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called

    @pytest.mark.asyncio
    async def get_site_incomplete_filters_test(self):
        client_id = 72959
        site_id = 343443
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_site = CoroutineMock()

        event_bus_request = {
            "request_id": 19,
            "body": {
                "client_id": client_id
            },
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify "site_id" in the body',
            'status': 400
        }

        get_site = GetSite(logger, event_bus, bruin_repository)
        await get_site.get_site(event_bus_request)
        bruin_repository.get_site.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called

    @pytest.mark.asyncio
    async def get_site_incomplete_filters_site_id_test(self):
        client_id = 72959
        site_id = 343443
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_site = CoroutineMock()

        event_bus_request = {
            "request_id": 19,
            "body": {
                "site_id": site_id
            },
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            'body': 'You must specify "client_id" in the body',
            'status': 400
        }

        get_site = GetSite(logger, event_bus, bruin_repository)
        await get_site.get_site(event_bus_request)
        bruin_repository.get_site.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        assert logger.error.called
