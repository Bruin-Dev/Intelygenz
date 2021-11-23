from unittest.mock import Mock

import pytest
from application.actions.post_outage_ticket import PostOutageTicket
from asynctest import CoroutineMock


class TestPostOutageTicket:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        post_outage_ticket = PostOutageTicket(logger, event_bus, bruin_repository)

        assert post_outage_ticket._logger is logger
        assert post_outage_ticket._event_bus is event_bus
        assert post_outage_ticket._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_outage_ticket_with_missing_client_id_test(self):
        logger = Mock()

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = CoroutineMock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        parameters = {
            "service_number": "VC05400009999"
        }
        response_topic = "some.topic"
        event_bus_request = {"request_id": 123, "response_topic": response_topic, "body": parameters}

        post_outage_ticket = PostOutageTicket(logger, event_bus, bruin_repository)

        await post_outage_ticket.post_outage_ticket(event_bus_request)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(
            "some.topic",
            {
                "request_id": 123,
                "status": 400,
                "body": 'Must specify "client_id" and "service_number" to post an outage ticket',
            },
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_with_missing_service_number_test(self):
        logger = Mock()

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = CoroutineMock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        parameters = {
            "client_id": 9994,
        }
        response_topic = "some.topic"
        event_bus_request = {"request_id": 123, "response_topic": response_topic, "body": parameters}

        post_outage_ticket = PostOutageTicket(logger, event_bus, bruin_repository)

        await post_outage_ticket.post_outage_ticket(event_bus_request)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(
            "some.topic",
            {
                "request_id": 123,
                "status": 400,
                "body": 'Must specify "client_id" and "service_number" to post an outage ticket',
            },
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_with_missing_body_test(self):
        logger = Mock()

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = CoroutineMock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        response_topic = "some.topic"
        event_bus_request = {"request_id": 123, "response_topic": response_topic}

        post_outage_ticket = PostOutageTicket(logger, event_bus, bruin_repository)

        await post_outage_ticket.post_outage_ticket(event_bus_request)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(
            "some.topic",
            {
                "request_id": 123,
                "status": 400,
                "body": 'Must include "body" in request',
            },
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_with_invalid_client_id_test(self):
        logger = Mock()

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = CoroutineMock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        parameters = {
            "client_id": None,
            "service_number": "VC05400009999"
        }
        response_topic = "some.topic"
        event_bus_request = {"request_id": 123, "response_topic": response_topic, "body": parameters}

        post_outage_ticket = PostOutageTicket(logger, event_bus, bruin_repository)

        await post_outage_ticket.post_outage_ticket(event_bus_request)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(
            "some.topic",
            {
                "request_id": 123,
                "status": 400,
                "body": '"client_id" and "service_number" must have non-null values',
            },
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_with_invalid_client_id_test(self):
        logger = Mock()

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = CoroutineMock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        parameters = {
            "client_id": 9994,
            "service_number": None
        }
        response_topic = "some.topic"
        event_bus_request = {"request_id": 123, "response_topic": response_topic, "body": parameters}

        post_outage_ticket = PostOutageTicket(logger, event_bus, bruin_repository)

        await post_outage_ticket.post_outage_ticket(event_bus_request)

        bruin_repository.post_outage_ticket.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(
            "some.topic",
            {
                "request_id": 123,
                "status": 400,
                "body": '"client_id" and "service_number" must have non-null values',
            },
        )

    @pytest.mark.asyncio
    async def post_outage_ticket_successful_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        outage_ticket_id = 123456
        response_status_code = 200

        repository_response = {
            'body': outage_ticket_id,
            'status': response_status_code,
        }

        logger = Mock()

        bruin_repository = Mock()
        bruin_repository.post_outage_ticket = CoroutineMock(return_value=repository_response)

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        parameters = {
            "client_id": client_id,
            "service_number": service_number
        }
        response_topic = "some.topic"
        event_bus_request = {"request_id": 123, "response_topic": response_topic, "body": parameters}

        post_outage_ticket = PostOutageTicket(logger, event_bus, bruin_repository)

        await post_outage_ticket.post_outage_ticket(event_bus_request)

        bruin_repository.post_outage_ticket.assert_awaited_once_with(client_id, service_number)
        event_bus.publish_message.assert_awaited_once_with(
            "some.topic",
            {
                "request_id": 123,
                **repository_response,
            },
        )
