from unittest.mock import Mock

import pytest
from application.actions.get_ticket_overview import GetTicketOverview
from asynctest import CoroutineMock

from config import testconfig as config


class TestGetTicketOverview:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        bruin_ticket_response = GetTicketOverview(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)

        assert bruin_ticket_response._logger is logger
        assert bruin_ticket_response._config is config.BRUIN_CONFIG
        assert bruin_ticket_response._event_bus is event_bus
        assert bruin_ticket_response._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_ticket_overview_test(self):
        logger = Mock()
        filtered_tickets_list = {'ticket_id': 123}
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        msg = {
            'request_id': request_id,
            'body': filtered_tickets_list,
            'response_topic': response_topic,
        }

        response_to_publish_in_topic = {
            'body': filtered_tickets_list,
            'status': 200
        }
        ticket_overview_mock = {'body': filtered_tickets_list, 'status': 200}
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_overview = CoroutineMock(return_value=ticket_overview_mock)

        bruin_ticket_response = GetTicketOverview(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_ticket_overview(msg)

        bruin_ticket_response._event_bus.publish_message.assert_awaited_once_with(
            response_topic, response_to_publish_in_topic
        )

    @pytest.mark.asyncio
    async def get_ticket_overview_not_body_test(self):
        logger = Mock()
        filtered_tickets_list = {'ticket_id': 123}
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_overview = CoroutineMock(return_value={'body': filtered_tickets_list,
                                                                           'status': 200})

        bruin_ticket_response = GetTicketOverview(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_ticket_overview(msg)

        bruin_ticket_response._bruin_repository.get_ticket_overview.assert_not_awaited()

    @pytest.mark.asyncio
    async def get_ticket_overview_not_ticket_id_test(self):
        logger = Mock()
        filtered_tickets_list = {}
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        msg = {
            'request_id': request_id,
            'body': filtered_tickets_list,
            'response_topic': response_topic,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_overview = CoroutineMock(return_value={'body': filtered_tickets_list,
                                                                           'status': 200})

        bruin_ticket_response = GetTicketOverview(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_ticket_overview(msg)

        bruin_ticket_response._bruin_repository.get_ticket_overview.assert_not_awaited()
