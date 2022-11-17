from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_tickets import GetTicket
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetTicket:
    def instance_test(self):
        bruin_repository = Mock()

        get_all_tickets = GetTicket(bruin_repository)

        assert get_all_tickets._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_all_tickets_with_ticket_id_defined_in_msg_200_test(self):
        filtered_tickets_list = [{"ticketID": 123}]

        client_id = 123
        ticket_id = 321

        category = "SD-WAN"
        ticket_topic = "VOO"

        ticket_status_list = ["New", "In-Progress"]
        msg = {
            "body": {
                "client_id": client_id,
                "ticket_id": ticket_id,
                "category": category,
                "ticket_topic": ticket_topic,
                "ticket_status": ticket_status_list,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        response_to_publish_in_topic = {"body": filtered_tickets_list, "status": 200}
        param_copy = msg["body"].copy()
        param_copy["product_category"] = param_copy["category"]
        del [param_copy["category"]]
        del [param_copy["ticket_status"]]

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = AsyncMock(
            return_value={"body": filtered_tickets_list, "status": 200}
        )

        get_all_tickets = GetTicket(bruin_repository)
        await get_all_tickets(request_msg)

        bruin_repository.get_all_filtered_tickets.assert_awaited_once_with(param_copy, ticket_status_list)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_to_publish_in_topic))

    @pytest.mark.asyncio
    async def get_all_tickets_with_service_number_defined_test(self):
        client_id = 123
        service_number = "VC1234567"
        category = "SD-WAN"
        ticket_topic = "VOO"
        ticket_status_list = ["New", "In-Progress"]

        repository_params = {
            "client_id": client_id,
            "service_number": service_number,
            "category": category,
            "ticket_topic": ticket_topic,
        }
        request_params = {
            **repository_params,
            "ticket_status": ticket_status_list,
        }

        filtered_tickets_list = [
            {"ticketID": 123},
        ]

        msg = {
            "body": request_params,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        repository_response = {"body": filtered_tickets_list, "status": 200}
        response_msg = {
            **repository_response,
        }

        param_copy = repository_params.copy()
        param_copy["product_category"] = param_copy["category"]
        del [param_copy["category"]]

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = AsyncMock(return_value=repository_response)

        get_all_tickets = GetTicket(bruin_repository)
        await get_all_tickets(request_msg)

        bruin_repository.get_all_filtered_tickets.assert_awaited_once_with(param_copy, ticket_status_list)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_msg))

    @pytest.mark.asyncio
    async def get_all_tickets_with_no_category_test(self):
        filtered_tickets_list = [{"ticketID": 123}, {"ticketID": 321}]

        client_id = 123

        ticket_topic = "VOO"

        ticket_status_list = ["New", "In-Progress"]
        msg = {
            "body": {
                "client_id": client_id,
                "ticket_topic": ticket_topic,
                "ticket_status": ticket_status_list,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        response_to_publish_in_topic = {"body": filtered_tickets_list, "status": 200}

        param_copy = msg["body"].copy()
        del [param_copy["ticket_status"]]

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = AsyncMock(
            return_value={"body": filtered_tickets_list, "status": 200}
        )

        get_all_tickets = GetTicket(bruin_repository)
        await get_all_tickets(request_msg)

        bruin_repository.get_all_filtered_tickets.assert_awaited_once_with(param_copy, ticket_status_list)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_to_publish_in_topic))

    @pytest.mark.asyncio
    async def get_all_tickets_with_no_ticket_id_test(self):
        filtered_tickets_list = [{"ticketID": 123}, {"ticketID": 321}]

        client_id = 123

        category = "SD-WAN"
        ticket_topic = "VOO"

        ticket_status_list = ["New", "In-Progress"]
        msg = {
            "body": {
                "client_id": client_id,
                "category": category,
                "ticket_topic": ticket_topic,
                "ticket_status": ticket_status_list,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        param_copy = msg["body"].copy()
        param_copy["product_category"] = param_copy["category"]
        del [param_copy["category"]]
        del [param_copy["ticket_status"]]

        response_to_publish_in_topic = {"body": filtered_tickets_list, "status": 200}

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = AsyncMock(
            return_value={"body": filtered_tickets_list, "status": 200}
        )

        get_all_tickets = GetTicket(bruin_repository)
        await get_all_tickets(request_msg)

        bruin_repository.get_all_filtered_tickets.assert_awaited_once_with(param_copy, ticket_status_list)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_to_publish_in_topic))

    @pytest.mark.asyncio
    async def get_tickets_with_date_test(self):
        client_id = 123

        filtered_tickets_list = [
            {
                "clientID": client_id,
                "clientName": "Sterling Jewelers, Inc.",
                "ticketID": 4767858,
                "category": "SD-WAN",
                "topic": "Service Outage Trouble",
                "referenceTicketNumber": 0,
                "ticketStatus": "New",
                "createDate": "8/20/2020 3:31:00 AM",
                "createdBy": "Intelygenz Ai",
                "creationNote": None,
                "resolveDate": "",
                "resolvedby": None,
                "closeDate": None,
                "closedBy": None,
                "lastUpdate": None,
                "updatedBy": None,
                "mostRecentNote": "8/20/2020 3:31:03 AM Intelygenz Ai",
                "nextScheduledDate": "8/26/2020 4:00:00 AM",
                "flags": "",
                "severity": "2",
            },
            {
                "clientID": client_id,
                "clientName": "Sterling Jewelers, Inc.",
                "ticketID": 4767346,
                "category": "SIP Trunking",
                "topic": "Service Outage Trouble",
                "referenceTicketNumber": 0,
                "ticketStatus": "In-Progress",
                "createDate": "8/19/2020 8:13:00 PM",
                "createdBy": "Jerald Beard",
                "creationNote": None,
                "resolveDate": "",
                "resolvedby": None,
                "closeDate": None,
                "closedBy": None,
                "lastUpdate": None,
                "updatedBy": None,
                "mostRecentNote": "8/19/2020 9:17:19 PM Richard Jordan",
                "nextScheduledDate": "8/21/2020 5:11:42 AM",
                "flags": "Frozen,Frozen",
                "severity": "2",
            },
        ]

        category = "SD-WAN"
        ticket_topic = "VOO"

        ticket_status_list = ["New", "In-Progress"]
        msg = {
            "body": {
                "client_id": client_id,
                "category": category,
                "ticket_topic": ticket_topic,
                "ticket_status": ticket_status_list,
                "start_date": "2020-8-19T20:12:00Z",
                "end_date": "2020-8-20T20:12:00Z",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        param_copy = msg["body"].copy()
        param_copy["product_category"] = param_copy["category"]
        del [param_copy["category"]]
        del [param_copy["ticket_status"]]

        response_to_publish_in_topic = {"body": filtered_tickets_list, "status": 200}

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = AsyncMock(
            return_value={"body": filtered_tickets_list, "status": 200}
        )

        get_all_tickets = GetTicket(bruin_repository)
        await get_all_tickets(request_msg)

        bruin_repository.get_all_filtered_tickets.assert_awaited_once_with(param_copy, ticket_status_list)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_to_publish_in_topic))

    @pytest.mark.asyncio
    async def get_all_tickets_missing_keys_in_params_test(self):
        filtered_tickets_list = [{"ticketID": 123}, {"ticketID": 321}]

        category = "SD-WAN"
        ticket_topic = "VOO"

        ticket_status_list = ["New", "In-Progress"]
        msg = {
            "body": {
                "category": category,
                "ticket_topic": ticket_topic,
                "ticket_status": ticket_status_list,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        response_to_publish_in_topic = {
            "body": "You must specify "
            '{..."body:{"client_id", "ticket_topic",'
            ' "ticket_status":[list of statuses]}...} in the request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = AsyncMock(
            return_value={"body": filtered_tickets_list, "status": 200}
        )

        get_all_tickets = GetTicket(bruin_repository)
        await get_all_tickets(request_msg)

        bruin_repository.get_all_filtered_tickets.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_to_publish_in_topic))

    @pytest.mark.asyncio
    async def get_all_tickets_missing_body_test(self):
        filtered_tickets_list = [{"ticketID": 123}, {"ticketID": 321}]

        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        response_to_publish_in_topic = {
            "body": 'Must include "body" in request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = AsyncMock(
            return_value={"body": filtered_tickets_list, "status": 200}
        )

        get_all_tickets = GetTicket(bruin_repository)
        await get_all_tickets(request_msg)

        bruin_repository.get_all_filtered_tickets.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(response_to_publish_in_topic))
