from unittest.mock import Mock

import pytest
from application.actions.get_tickets_basic_info import GetTicketsBasicInfo
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()


class TestGetTicketsBasicInfo:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        action = GetTicketsBasicInfo(logger, event_bus, bruin_repository)

        assert action._logger is logger
        assert action._event_bus is event_bus
        assert action._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_tickets_basic_info_ok_test(self):
        ticket_statuses = [
            "New",
            "In-Progress",
            "Draft",
        ]
        shared_payload = {
            "client_id": 9994,
            "service_number": "VC1234567",
            "product_category": "SD-WAN",
            "ticket_topic": "VAS",
            "start_date": "2020-08-19T20:12:00Z",
            "end_date": "2020-08-20T20:12:00Z",
        }
        bruin_payload = {
            **shared_payload,
            "ticket_statuses": ticket_statuses,
        }

        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request_message = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": bruin_payload,
        }

        tickets_response = {
            "body": [
                {
                    "clientID": 9994,
                    "ticketID": 5262293,
                    "ticketStatus": "New",
                    "address": {
                        "address": "1090 Vermont Ave NW",
                        "city": "Washington",
                        "state": "DC",
                        "zip": "20005-4905",
                        "country": "USA",
                    },
                    "createDate": "3/13/2021 12:59:36 PM",
                },
            ],
            "status": 200,
        }
        response_message = {
            "request_id": uuid_,
            **tickets_response,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets_basic_info = CoroutineMock(return_value=tickets_response)

        action = GetTicketsBasicInfo(logger, event_bus, bruin_repository)

        await action.get_tickets_basic_info(request_message)

        bruin_repository.get_tickets_basic_info.assert_awaited_once_with(shared_payload, ticket_statuses)
        event_bus.publish_message.assert_awaited_once_with(response_topic, response_message)

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_body_missing_in_request_message_test(self):
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request_message = {
            "request_id": uuid_,
            "response_topic": response_topic,
        }

        response_message = {
            "request_id": uuid_,
            "body": 'Must include "body" in the request message',
            "status": 400,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets_basic_info = CoroutineMock()

        action = GetTicketsBasicInfo(logger, event_bus, bruin_repository)

        await action.get_tickets_basic_info(request_message)

        bruin_repository.get_tickets_basic_info.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response_message)

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_ticket_statuses_missing_in_request_body_test(self):
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        request_message = {
            "request_id": uuid_,
            "response_topic": response_topic,
            "body": {
                "service_number": "VC1234567",
                "product_category": "SD-WAN",
                "ticket_topic": "VAS",
                "start_date": "2020-08-19T20:12:00Z",
                "end_date": "2020-08-20T20:12:00Z",
            },
        }

        response_message = {
            "request_id": uuid_,
            "body": 'Must specify "ticket_statuses" in the body of the request',
            "status": 400,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_tickets_basic_info = CoroutineMock()

        action = GetTicketsBasicInfo(logger, event_bus, bruin_repository)

        await action.get_tickets_basic_info(request_message)

        bruin_repository.get_tickets_basic_info.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(response_topic, response_message)
