from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories.bruin_repository import BruinRepository
from asynctest import CoroutineMock


class TestBruinRepository:

    def instance_test(self):
        logger = Mock()
        bruin_client = Mock()

        bruin_repository = BruinRepository(logger, bruin_client)

        assert bruin_repository._logger is logger
        assert bruin_repository._bruin_client is bruin_client

    @pytest.mark.asyncio
    async def get_all_filtered_tickets_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = CoroutineMock(side_effect=[
            {'body': [{'ticketID': 123}, {'ticketID': 123}], 'status': 200},
            {'body': [{'ticketID': 321}], 'status': 200}
        ])
        params = dict(client_id=123, ticket_id=321, category='SD-WAN', ticket_topic='VOO')

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"

        full_params_1 = params.copy()
        full_params_1["TicketStatus"] = ticket_status_1

        full_params_2 = params.copy()
        full_params_2["TicketStatus"] = ticket_status_2

        bruin_repository = BruinRepository(logger, bruin_client)
        filtered_tickets = await bruin_repository.get_all_filtered_tickets(
            params=params,
            ticket_status=[ticket_status_1, ticket_status_2],
        )

        bruin_repository._bruin_client.get_all_tickets.assert_awaited()
        ticket_item1 = {'ticketID': 123}
        ticket_item2 = {'ticketID': 321}
        assert ticket_item1 in filtered_tickets['body']
        assert ticket_item2 in filtered_tickets['body']
        assert filtered_tickets['status'] == 200

    @pytest.mark.asyncio
    async def get_all_filtered_tickets_with_none_returned_for_one_ticket_status_test(self):
        ticket_1_id = 123
        ticket_2_id = 321
        ticket_3_id = 456
        ticket_4_id = 654

        tickets_response_body_1 = [
            {'ticketID': 123},
            {'ticketID': 321},
        ]
        tickets_response_body_2 = []
        tickets_response_body_3 = [
            {'ticketID': 456},
            {'ticketID': 654},
        ]

        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = CoroutineMock(side_effect=[
            {'body': tickets_response_body_1, 'status': 200},
            {'body': tickets_response_body_2, 'status': 404},
            {'body': tickets_response_body_3, 'status': 200},
        ])
        params = dict(client_id=123, ticket_id=321, category='SD-WAN', ticket_topic='VOO')

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_status_3 = "Yet-Another-Status"

        full_params_1 = params.copy()
        full_params_1["TicketStatus"] = ticket_status_1

        full_params_2 = params.copy()
        full_params_2["TicketStatus"] = ticket_status_2

        full_params_3 = params.copy()
        full_params_3["TicketStatus"] = ticket_status_3

        bruin_repository = BruinRepository(logger, bruin_client)

        response = dict.fromkeys(["body", "status"])
        response['body'] = []
        response['status'] = 200

        async def gather_mock(*args, **kwargs):
            results = []
            results.append(await bruin_repository._get_tickets_by_status(ticket_status_1, params.copy(), response))
            results.append(await bruin_repository._get_tickets_by_status(ticket_status_2, params.copy(), response))
            results.append(await bruin_repository._get_tickets_by_status(ticket_status_3, params.copy(), response))
            return results

        with patch.object(bruin_repository_module.asyncio, "gather", return_value=gather_mock()):
            filtered_tickets = await bruin_repository.get_all_filtered_tickets(
                params=params,
                ticket_status=[ticket_status_1, ticket_status_2, ticket_status_3]
            )

            bruin_client.get_all_tickets.assert_has_awaits([
                call(full_params_1),
                call(full_params_2),
                call(full_params_3),
            ], any_order=True)
            assert filtered_tickets == {
                'body': [
                    {'ticketID': ticket_1_id},
                    {'ticketID': ticket_2_id},
                    {'ticketID': ticket_3_id},
                    {'ticketID': ticket_4_id},
                ],
                'status': 200,
            }

    @pytest.mark.asyncio
    async def get_filtered_tickets_with_bruin_returning_empty_lists_for_every_status_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = CoroutineMock(side_effect=[
            {'body': [], 'status': 200},
            {'body': [], 'status': 200},
        ])

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"

        params = dict(client_id=123, ticket_id=321, category='SD-WAN', ticket_topic='VOO')

        full_params_1 = params.copy()
        full_params_1["TicketStatus"] = ticket_status_1

        full_params_2 = params.copy()
        full_params_2["TicketStatus"] = ticket_status_2

        bruin_repository = BruinRepository(logger, bruin_client)
        filtered_tickets = await bruin_repository.get_all_filtered_tickets(
            params=params,
            ticket_status=[ticket_status_1, ticket_status_2],
        )

        bruin_repository._bruin_client.get_all_tickets.assert_awaited()
        assert filtered_tickets['body'] == []
        assert filtered_tickets['status'] == 200

    @pytest.mark.asyncio
    async def get_ticket_details_test(self):
        logger = Mock()
        ticket_id = 123
        expected_ticket_details = 'Some Ticket Details'

        bruin_client = Mock()
        bruin_client.get_ticket_details = CoroutineMock(return_value=expected_ticket_details)

        bruin_repository = BruinRepository(logger, bruin_client)
        ticket_details = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._bruin_client.get_ticket_details.assert_awaited_once_with(ticket_id)
        assert ticket_details == expected_ticket_details

    @pytest.mark.asyncio
    async def post_ticket_note_test(self):
        logger = Mock()
        ticket_id = 123
        note_contents = 'TicketNote'
        payload = dict(note=note_contents)
        expected_post_response = 'Ticket Appended'

        bruin_client = Mock()
        bruin_client.post_ticket_note = CoroutineMock(return_value=expected_post_response)

        bruin_repository = BruinRepository(logger, bruin_client)
        post_response = await bruin_repository.post_ticket_note(ticket_id, note_contents)

        bruin_client.post_ticket_note.assert_awaited_once_with(ticket_id, payload)
        assert post_response == expected_post_response

    @pytest.mark.asyncio
    async def post_ticket_note_with_optional_service_numbers_list_test(self):
        ticket_id = 123
        service_numbers = ['VC1234567']
        note_contents = 'TicketNote'

        payload = {
            'note': note_contents,
            'serviceNumbers': service_numbers
        }

        expected_post_response = 'Ticket Appended'

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_ticket_note = CoroutineMock(return_value=expected_post_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        post_response = await bruin_repository.post_ticket_note(
            ticket_id, note_contents, service_numbers=service_numbers
        )

        bruin_client.post_ticket_note.assert_awaited_once_with(ticket_id, payload)
        assert post_response == expected_post_response

    @pytest.mark.asyncio
    async def post_ticket_test(self):
        logger = Mock()
        payload = dict(client_id=321, category='Some Category', notes=['List of Notes'],
                       services=['List of Services'], contacts=['List of Contacts'])
        expected_post_response = 'Ticket Created'

        bruin_client = Mock()
        bruin_client.post_ticket = CoroutineMock(return_value=expected_post_response)

        bruin_repository = BruinRepository(logger, bruin_client)
        create_ticket = await bruin_repository.post_ticket(payload)
        bruin_client.post_ticket.assert_awaited_once_with(payload)
        assert create_ticket == expected_post_response

    @pytest.mark.asyncio
    async def open_ticket_test(self):
        logger = Mock()

        ticket_id = 123
        detail_id = 321
        payload = dict(Status='O')
        successful_status_change = 'Success'

        bruin_client = Mock()
        bruin_client.update_ticket_status = CoroutineMock(return_value=successful_status_change)

        bruin_repository = BruinRepository(logger, bruin_client)
        change_status = await bruin_repository.open_ticket(ticket_id, detail_id)
        bruin_client.update_ticket_status.assert_awaited_once_with(ticket_id, detail_id, payload)
        assert change_status == successful_status_change

    @pytest.mark.asyncio
    async def resolve_ticket_test(self):
        logger = Mock()

        ticket_id = 123
        detail_id = 321
        payload = dict(Status='R')
        successful_status_change = 'Success'

        bruin_client = Mock()
        bruin_client.update_ticket_status = CoroutineMock(return_value=successful_status_change)

        bruin_repository = BruinRepository(logger, bruin_client)
        change_status = await bruin_repository.resolve_ticket(ticket_id, detail_id)
        bruin_client.update_ticket_status.assert_awaited_once_with(ticket_id, detail_id, payload)
        assert change_status == successful_status_change

    @pytest.mark.asyncio
    async def get_management_status_ok_test(self):
        logger = Mock()
        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
        }
        response = {
            "body":
                {
                    "inventoryId": "12796795",
                    "serviceNumber": "VC05400002265",
                    "attributes": [
                        {
                            "key": "Management Status",
                            "value": "Active – Platinum Monitoring"
                        }
                    ]
                },
            "status": 200,
        }
        bruin_client = Mock()
        bruin_client.get_management_status = CoroutineMock(return_value=response)
        bruin_repository = BruinRepository(logger, bruin_client)
        response = await bruin_repository.get_management_status(filters)
        management_status = response["body"]
        bruin_client.get_management_status.assert_awaited_once_with(filters)
        assert "Active – Platinum Monitoring" in management_status

    @pytest.mark.asyncio
    async def get_management_status_no_attributes_test(self):
        logger = Mock()
        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
        }
        response = {
            "body":
                {
                    "inventoryId": "12796795",
                    "serviceNumber": "VC05400002265",
                },
            "status": 200,
        }
        bruin_client = Mock()
        bruin_client.get_management_status = CoroutineMock(return_value=response)
        bruin_repository = BruinRepository(logger, bruin_client)
        response_management = await bruin_repository.get_management_status(filters)
        bruin_client.get_management_status.assert_awaited_once_with(filters)
        assert response_management == response

    @pytest.mark.asyncio
    async def get_management_status_ok_no_management_key_test(self):
        logger = Mock()
        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
        }
        response = {
            "body":
                {
                    "inventoryId": "12796795",
                    "serviceNumber": "VC05400002265",
                    "attributes": [
                        {
                            "key": "RD1.K3",
                            "value": "RD Circuit information"
                        }
                    ]
                },
            "status": 200,
        }
        bruin_client = Mock()
        bruin_client.get_management_status = CoroutineMock(return_value=response)
        bruin_repository = BruinRepository(logger, bruin_client)
        response = await bruin_repository.get_management_status(filters)
        management_status = response["body"]
        bruin_client.get_management_status.assert_awaited_once_with(filters)
        assert management_status is None

    @pytest.mark.asyncio
    async def get_management_status_400_test(self):
        logger = Mock()
        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999"
        }
        response = {
            "body": "empty",
            "status": 400
        }
        bruin_client = Mock()
        bruin_client.get_management_status = CoroutineMock(return_value=response)
        bruin_repository = BruinRepository(logger, bruin_client)
        management_status = await bruin_repository.get_management_status(filters)
        bruin_client.get_management_status.assert_awaited_once_with(filters)
        assert management_status == response

    @pytest.mark.asyncio
    async def get_management_status_ko_test(self):
        logger = Mock()
        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
        }
        response = {
            "body": "empty",
            "status": 500
        }
        bruin_client = Mock()
        bruin_client.get_management_status = CoroutineMock(return_value=response)
        bruin_repository = BruinRepository(logger, bruin_client)
        management_status = await bruin_repository.get_management_status(filters)
        bruin_client.get_management_status.assert_awaited_once_with(filters)
        assert management_status == response

    @pytest.mark.asyncio
    async def post_outage_ticket_with_2XX_status_code_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        ticket_id = 4503440
        response_status = 200
        client_response = {
            "body": {
                "ticketId": ticket_id,
                "inventoryId": 12796795,
                "wtn": service_number,
                "errorMessage": None,
                "errorCode": 0,
            },
            "status": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_awaited_once_with(client_id, service_number)
        assert result == {"body": ticket_id, "status": response_status}

    @pytest.mark.asyncio
    async def post_outage_ticket_with_409_status_code_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        ticket_id = 4503440
        response_status = 409
        client_response = {
            "body": {
                "ticketId": ticket_id,
                "inventoryId": 12796795,
                "wtn": service_number,
                "errorMessage": None,
                "errorCode": response_status,
            },
            "status": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_awaited_once_with(client_id, service_number)
        assert result == {"body": ticket_id, "status": response_status}

    @pytest.mark.asyncio
    async def post_outage_ticket_with_471_status_code_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        ticket_id = 4503440
        response_status = 471
        client_response = {
            "body": {
                "ticketId": ticket_id,
                "inventoryId": 12796795,
                "wtn": service_number,
                "errorMessage": None,
                "errorCode": response_status,
            },
            "status": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_awaited_once_with(client_id, service_number)
        assert result == {"body": ticket_id, "status": response_status}

    @pytest.mark.asyncio
    async def post_outage_ticket_with_472_status_code_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        ticket_id = 4503440
        response_status = 472
        client_response = {
            "body": {
                "ticketId": ticket_id,
                "inventoryId": 12796795,
                "wtn": service_number,
                "errorMessage": None,
                "errorCode": response_status,
            },
            "status": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_awaited_once_with(client_id, service_number)
        assert result == {"body": ticket_id, "status": response_status}

    @pytest.mark.asyncio
    async def post_outage_ticket_with_473_status_code_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        ticket_id = 4503440
        response_status = 473
        client_response = {
            "body": {
                "ticketId": ticket_id,
                "inventoryId": 12796795,
                "wtn": service_number,
                "errorMessage": None,
                "errorCode": response_status,
            },
            "status": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_awaited_once_with(client_id, service_number)
        assert result == {"body": ticket_id, "status": response_status}

    @pytest.mark.asyncio
    async def post_outage_ticket_with_error_status_code_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        response_status = 500
        client_response = {
            "body": "Got internal error from Bruin",
            "status": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_awaited_once_with(client_id, service_number)
        assert result == client_response

    @pytest.mark.asyncio
    async def get_client_info_with_error_status_code_test(self):
        filters = {
            'service_number': "VC019191",
            'status': 'A'
        }

        response_status = 400
        client_response = {
            "body": {
                "errors": {
                    "clientId": [
                        "The value is not valid."
                    ]
                },
                "type": None,
                "title": "Invalid arguments to the API",
                "status": 400,
                "detail": "The inputs supplied to the API are invalid",
                "instance": "/api/Inventory",
                "extensions": {}
            },
            "status": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_client_info = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_client_info(filters)

        bruin_client.get_client_info.assert_awaited_once_with(filters)
        assert result == client_response

    @pytest.mark.asyncio
    async def get_client_info_with_2XX_test(self):
        filters = {
            'service_number': "VC019191",
            'status': 'A'
        }

        response_status = 200
        client_response = {
            "body": {
                "documents": [
                    {
                        "clientID": 9919,
                        "clientName": "Tet Corp",
                        "vendor": "Central Positronics",
                        "accountNumber": "59864",
                        "subAccountNumber": "4554",
                        "inventoryID": "12295777",
                        "serviceNumber": "VC01919",
                        "siteId": 16199,
                        "siteLabel": "Turtle Square",
                        "address": {
                            "address": "2125 Fake Street",
                            "city": "River Crossing",
                            "state": "ST",
                            "zip": "1999556",
                            "country": "MEJIS"
                        },
                        "hierarchy": "|Tet Corp|River Crossing|SomeSite|",
                        "costCenter": "15830",
                        "assignee": None,
                        "description": "",
                        "installDate": "2018-04-03T17:58:51Z",
                        "disconnectDate": None,
                        "status": "A",
                        "verified": "Y",
                        "productCategory": "SD-WAN",
                        "productType": "SD-WAN",
                        "items": [
                            {
                                "itemName": "Licensed Software - SD-WAN 30M",
                                "primaryIndicator": "SD-WAN"
                            }
                        ],
                        "contractIdentifier": None,
                        "rateCardIdentifier": None,
                        "lastInvoiceUsageDate": "2020-02-23T05:00:00Z",
                        "lastUsageDate": None,
                        "longitude": -76.265384,
                        "latitude": 36.843456
                    }
                ]
            },
            "status": response_status,
        }

        expected_result = {
            "body": {"client_id": client_response["body"]["documents"][0]["clientID"],
                     "client_name": client_response["body"]["documents"][0]["clientName"]},
            "status": response_status
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_client_info = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_client_info(filters)

        bruin_client.get_client_info.assert_awaited_once_with(filters)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_client_info_with_2XX_empty_documents_test(self):
        filters = {
            'service_number': "VC019191",
            'status': 'A'
        }

        response_status = 200
        client_response = {
            "body": {
                "documents": []
            },
            "status": response_status,
        }

        expected_result = {
            "body": {"client_id": None,
                     "client_name": None},
            "status": response_status
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_client_info = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_client_info(filters)

        bruin_client.get_client_info.assert_awaited_once_with(filters)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_client_info_with_2XX_no_active_edge_test(self):
        filters = {
            'service_number': "VC019191",
            'status': 'A'
        }

        response_status = 200
        client_response = {
            "body": {
                "documents": [
                    {
                        "clientID": 9919,
                        "clientName": "Tet Corp",
                        "vendor": "Central Positronics",
                        "accountNumber": "59864",
                        "subAccountNumber": "4554",
                        "inventoryID": "12295777",
                        "serviceNumber": "VC01919",
                        "siteId": 16199,
                        "siteLabel": "Turtle Square",
                        "address": {
                            "address": "2125 Fake Street",
                            "city": "River Crossing",
                            "state": "ST",
                            "zip": "1999556",
                            "country": "MEJIS"
                        },
                        "hierarchy": "|Tet Corp|River Crossing|SomeSite|",
                        "costCenter": "15830",
                        "assignee": None,
                        "description": "",
                        "installDate": "2018-04-03T17:58:51Z",
                        "disconnectDate": "2018-04-03T18:00:51Z",
                        "status": "D",
                        "verified": "Y",
                        "productCategory": "SD-WAN",
                        "productType": "SD-WAN",
                        "items": [
                            {
                                "itemName": "Licensed Software - SD-WAN 30M",
                                "primaryIndicator": "SD-WAN"
                            }
                        ],
                        "contractIdentifier": None,
                        "rateCardIdentifier": None,
                        "lastInvoiceUsageDate": "2020-02-23T05:00:00Z",
                        "lastUsageDate": None,
                        "longitude": -76.265384,
                        "latitude": 36.843456
                    }
                ]
            },
            "status": response_status,
        }

        expected_result = {
            "body": {"client_id": None,
                     "client_name": None},
            "status": response_status
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_client_info = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_client_info(filters)

        bruin_client.get_client_info.assert_awaited_once_with(filters)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_client_info_with_2XX_different_serial_number_than_provided(self):
        filters = {
            'service_number': "VC019191",
            'status': 'A'
        }

        response_status = 200
        client_response = {
            "body": {
                "documents": [
                    {
                        "clientID": 9919,
                        "clientName": "Tet Corp",
                        "vendor": "Central Positronics",
                        "accountNumber": "59864",
                        "subAccountNumber": "4554",
                        "inventoryID": "12295777",
                        "serviceNumber": "VC01919-RET",
                        "siteId": 16199,
                        "siteLabel": "Turtle Square",
                        "address": {
                            "address": "2125 Fake Street",
                            "city": "River Crossing",
                            "state": "ST",
                            "zip": "1999556",
                            "country": "MEJIS"
                        },
                        "hierarchy": "|Tet Corp|River Crossing|SomeSite|",
                        "costCenter": "15830",
                        "assignee": None,
                        "description": "",
                        "installDate": "2018-04-03T17:58:51Z",
                        "disconnectDate": None,
                        "status": "A",
                        "verified": "Y",
                        "productCategory": "SD-WAN",
                        "productType": "SD-WAN",
                        "items": [
                            {
                                "itemName": "Licensed Software - SD-WAN 30M",
                                "primaryIndicator": "SD-WAN"
                            }
                        ],
                        "contractIdentifier": None,
                        "rateCardIdentifier": None,
                        "lastInvoiceUsageDate": "2020-02-23T05:00:00Z",
                        "lastUsageDate": None,
                        "longitude": -76.265384,
                        "latitude": 36.843456
                    }
                ]
            },
            "status": response_status,
        }

        expected_result = {
            "body": {"client_id": None,
                     "client_name": None},
            "status": response_status
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_client_info = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_client_info(filters)

        bruin_client.get_client_info.assert_awaited_once_with(filters)
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_test(self):
        ticket_id = 4503440
        detail_id = 4806634
        service_number = 'VC05400002265'

        work_queue_filters = {
            "ServiceNumber": service_number,
            "DetailId": detail_id,
        }

        next_results_response = {
            'body': [
                {
                    "resultTypeId": 620,
                    "resultName": "No Trouble Found - Carrier Issue",
                    "notes": [
                        {
                            "noteType": "Notes",
                            "noteDescription": "Notes",
                            "availableValueOptions": None,
                            "defaultValue": None,
                            "required": False,
                        }
                    ]
                }
            ],
            'status': 200,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_possible_detail_next_result = CoroutineMock(return_value=next_results_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_next_results_for_ticket_detail(ticket_id, detail_id, service_number)

        bruin_client.get_possible_detail_next_result.assert_awaited_once_with(ticket_id, work_queue_filters)
        assert result == next_results_response

    @pytest.mark.asyncio
    async def change_detail_work_queue_with_retrieval_of_possible_work_queues_returning_non_2xx_status_test(self):
        ticket_id = 4503440
        detail_id = 4806634
        service_number = 'VC05400002265'
        filters = {
            "service_number": service_number,
            "detail_id": detail_id,
            "queue_name": "Repair Completed",
        }

        work_queue_filters = {
            "ServiceNumber": service_number,
            "DetailId": detail_id,
        }

        possible_work_queues_response_body = 'Got internal error from Bruin'
        possible_work_queues_response_status = 500
        possible_work_queues_response = {
            "body": possible_work_queues_response_body,
            "status": possible_work_queues_response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_possible_detail_next_result = CoroutineMock(return_value=possible_work_queues_response)
        bruin_client.change_detail_work_queue = CoroutineMock()

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.change_detail_work_queue(ticket_id, filters)

        bruin_client.get_possible_detail_next_result.assert_awaited_once_with(ticket_id, work_queue_filters)
        bruin_client.change_detail_work_queue.assert_not_awaited()

        expected = {
            'body': f'Error while claiming possible work queues for ticket {ticket_id} and filters '
                    f'{work_queue_filters}: {possible_work_queues_response_body}',
            'status': possible_work_queues_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def change_detail_work_queue_with_no_work_queues_found_test(self):
        ticket_id = 4503440
        detail_id = 4806634
        service_number = 'VC05400002265'
        filters = {
            "service_number": service_number,
            "detail_id": detail_id,
            "queue_name": "Repair Completed",
        }

        work_queue_filters = {
            "ServiceNumber": service_number,
            "DetailId": detail_id,
        }

        possible_work_queues_response = {
            "body": {
                "currentTaskId": 10398903,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": []
            },
            "status": 200
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_possible_detail_next_result = CoroutineMock(return_value=possible_work_queues_response)
        bruin_client.change_detail_work_queue = CoroutineMock()

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.change_detail_work_queue(ticket_id, filters)

        bruin_client.get_possible_detail_next_result.assert_awaited_once_with(ticket_id, work_queue_filters)
        bruin_client.change_detail_work_queue.assert_not_awaited()

        expected = {
            'body': f'No work queues were found for ticket {ticket_id} and filters {work_queue_filters}',
            'status': 404,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def change_detail_work_queue_with_possible_work_queues_not_containing_target_queue_test(self):
        ticket_id = 4503440
        detail_id = 4806634
        service_number = 'VC05400002265'

        target_queue_name = "Repair Completed"
        filters = {
            "service_number": service_number,
            "detail_id": detail_id,
            "queue_name": target_queue_name,
        }

        work_queue_filters = {
            "ServiceNumber": service_number,
            "DetailId": detail_id,
        }

        work_queue = {
            "resultTypeId": 139,
            "resultName": "Another Queue",
            "notes": [
                {
                    "noteType": "RFO",
                    "noteDescription": "Reason for Outage",
                    "availableValueOptions": [
                        {
                            "text": "Area Wide Outage",
                            "value": "Area Wide Outage"
                        },
                    ]
                }
            ]
        }
        possible_work_queues_response = {
            "body": {
                "currentTaskId": 10398903,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    work_queue
                ]
            },
            "status": 200
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_possible_detail_next_result = CoroutineMock(return_value=possible_work_queues_response)
        bruin_client.change_detail_work_queue = CoroutineMock()

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.change_detail_work_queue(ticket_id, filters)

        bruin_client.get_possible_detail_next_result.assert_awaited_once_with(ticket_id, work_queue_filters)
        bruin_client.change_detail_work_queue.assert_not_awaited()

        expected = {
            "body": f'No work queue with name {target_queue_name} was found using ticket ID {ticket_id} and '
                    f'filters {work_queue_filters}',
            "status": 404
        }
        assert result == expected

    @pytest.mark.asyncio
    async def change_detail_work_queue_with_all_conditions_met_test(self):
        ticket_id = 4503440
        detail_id = 4806634
        service_number = 'VC05400002265'
        filters = {
            "service_number": service_number,
            "detail_id": detail_id,
            "queue_name": "Repair Completed",
        }

        work_queue_filters = {
            "ServiceNumber": service_number,
            "DetailId": detail_id,
        }

        work_queue_id = 139
        work_queue = {
            "resultTypeId": work_queue_id,
            "resultName": "Repair Completed",
            "notes": [
                {
                    "noteType": "RFO",
                    "noteDescription": "Reason for Outage",
                    "availableValueOptions": [
                        {
                            "text": "Area Wide Outage",
                            "value": "Area Wide Outage"
                        },
                    ]
                }
            ]
        }
        possible_work_queues_response = {
            "body": {
                "currentTaskId": 10398903,
                "currentTaskKey": "344",
                "currentTaskName": "Holmdel NOC Investigate ",
                "nextResults": [
                    work_queue
                ]
            },
            "status": 200
        }

        change_work_queue_payload = {
            "details": [
                {
                    "detailId": detail_id,
                    "serviceNumber": service_number,
                }
            ],
            "notes": [],
            "resultTypeId": work_queue_id,
        }
        change_work_queue_response = {
            "body": {
                "message": "success"
            },
            "status": 200
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_possible_detail_next_result = CoroutineMock(return_value=possible_work_queues_response)
        bruin_client.change_detail_work_queue = CoroutineMock(return_value=change_work_queue_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.change_detail_work_queue(ticket_id, filters)

        bruin_client.get_possible_detail_next_result.assert_awaited_once_with(ticket_id, work_queue_filters)
        bruin_client.change_detail_work_queue.assert_awaited_once_with(ticket_id, change_work_queue_payload)
        assert result == change_work_queue_response

    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_response_not_having_2xx_code_test(self):
        ticket_id = 12345
        notes = [
            {
                'text': 'Test note 1',
                'service_number': 'VC1234567',
            },
            {
                'text': 'Test note 2',
                'detail_id': 999,
            },
            {
                'text': 'Test note 3',
                'service_number': 'VC99999999',
                'detail_id': 888,
            },
            {
                'text': 'Test note 4',
                'service_number': 'VC12312312',
                'detail_id': 777,
                'is_private': True,
            },
        ]

        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 2',
                    'detailId': 999,
                },
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 3',
                    'serviceNumber': 'VC99999999',
                    'detailId': 888,
                },
                {
                    'noteType': 'CON',
                    'noteValue': 'Test note 4',
                    'serviceNumber': 'VC12312312',
                    'detailId': 777,
                },
            ],
        }

        client_response = {
            "body": 'Got internal error from Bruin',
            "status": 500,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_multiple_ticket_notes = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.post_multiple_ticket_notes(ticket_id, notes)

        bruin_client.post_multiple_ticket_notes.assert_awaited_once_with(ticket_id, payload)
        assert result == client_response

    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_all_conditions_met_test(self):
        ticket_id = 12345
        notes = [
            {
                'text': 'Test note 1',
                'service_number': 'VC1234567',
            },
            {
                'text': 'Test note 2',
                'detail_id': 999,
            },
            {
                'text': 'Test note 3',
                'service_number': 'VC99999999',
                'detail_id': 888,
            },
            {
                'text': 'Test note 4',
                'service_number': 'VC12312312',
                'detail_id': 777,
                'is_private': True,
            },
        ]

        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 2',
                    'detailId': 999,
                },
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 3',
                    'serviceNumber': 'VC99999999',
                    'detailId': 888,
                },
                {
                    'noteType': 'CON',
                    'noteValue': 'Test note 4',
                    'serviceNumber': 'VC12312312',
                    'detailId': 777,
                },
            ],
        }

        note_1_from_client_response = {
            "noteID": 70646090,
            "noteType": "ADN",
            "noteValue": "Test note 1",
            "actionID": None,
            "detailID": 5002307,
            "enteredBy": 442301,
            "enteredDate": "2020-05-20T06:00:38.803-04:00",
            "lastViewedBy": None,
            "lastViewedDate": None,
            "refNoteID": None,
            "noteStatus": None,
            "noteText": None,
            "childNotes": None,
            "documents": None,
            "alerts": None,
            "taggedUserDirIDs": None,
        }
        note_2_from_client_response = {
            "noteID": 70646091,
            "noteType": "ADN",
            "noteValue": "Test note 2",
            "actionID": None,
            "detailID": 999,
            "enteredBy": 442301,
            "enteredDate": "2020-05-20T06:00:38.803-04:00",
            "lastViewedBy": None,
            "lastViewedDate": None,
            "refNoteID": None,
            "noteStatus": None,
            "noteText": None,
            "childNotes": None,
            "documents": None,
            "alerts": None,
            "taggedUserDirIDs": None,
        }
        note_3_from_client_response = {
            "noteID": 70646091,
            "noteType": "ADN",
            "noteValue": "Test note 3",
            "actionID": None,
            "detailID": 888,
            "enteredBy": 442301,
            "enteredDate": "2020-05-20T06:00:38.803-04:00",
            "lastViewedBy": None,
            "lastViewedDate": None,
            "refNoteID": None,
            "noteStatus": None,
            "noteText": None,
            "childNotes": None,
            "documents": None,
            "alerts": None,
            "taggedUserDirIDs": None,
        }
        note_4_from_client_response = {
            "noteID": 70646091,
            "noteType": "CON",
            "noteValue": "Test note 4",
            "actionID": None,
            "detailID": 888,
            "enteredBy": 442301,
            "enteredDate": "2020-05-20T06:00:38.803-04:00",
            "lastViewedBy": None,
            "lastViewedDate": None,
            "refNoteID": None,
            "noteStatus": None,
            "noteText": None,
            "childNotes": None,
            "documents": None,
            "alerts": None,
            "taggedUserDirIDs": None,
        }
        client_response = {
            "body": {
                "ticketNotes": [
                    note_1_from_client_response,
                    note_2_from_client_response,
                    note_3_from_client_response,
                    note_4_from_client_response,
                ],
            },
            "status": 200,
        }
        repository_response = {
            "body": [
                note_1_from_client_response,
                note_2_from_client_response,
                note_3_from_client_response,
                note_4_from_client_response,
            ],
            "status": 200,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_multiple_ticket_notes = CoroutineMock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.post_multiple_ticket_notes(ticket_id, notes)

        bruin_client.post_multiple_ticket_notes.assert_awaited_once_with(ticket_id, payload)
        assert result == repository_response

    @pytest.mark.asyncio
    async def get_ticket_task_history_ok_test(self):
        ticket_id = 4503440

        results = ['List of task history']
        return_body = {'result': results}
        return_status = 200

        client_response = {
            "body": return_body,
            "status": return_status
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_ticket_task_history = CoroutineMock(return_value=client_response)

        filter = {'ticket_id': ticket_id}
        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_ticket_task_history(filter)

        bruin_client.get_ticket_task_history.assert_awaited_once_with(filter)
        assert result == {"body": results, "status": return_status}

    @pytest.mark.asyncio
    async def get_ticket_task_history_ko_non_2xx_return_test(self):
        ticket_id = 4503440

        return_body = 'Failed'
        return_status = 400

        client_response = {
            "body": return_body,
            "status": return_status
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_ticket_task_history = CoroutineMock(return_value=client_response)

        filter = {'ticket_id': ticket_id}
        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_ticket_task_history(filter)

        bruin_client.get_ticket_task_history.assert_awaited_once_with(filter)
        assert result == {"body": return_body, "status": return_status}

    @pytest.mark.asyncio
    async def get_ticket_overview_test(self):
        ticket_id = '4503440'
        return_status = 200

        logger = Mock()
        ticket_123 = {
            'ticketID': 123,
            "clientName": "Sam &amp; Su's Retail Shop 5",
            "category": "",
            "topic": "Add Cloud PBX User License",
            "referenceTicketNumber": 0,
            "ticketStatus": "Resolved",
            "address": {
                "address": "69 Blanchard St",
                "city": "Newark",
                "state": "NJ",
                "zip": "07105-4701",
                "country": "USA"
            },
            "createDate": "4/23/2019 7:59:50 PM",
            "createdBy": "Amulya Bidar Nataraj 113",
            "creationNote": 'null',
            "resolveDate": "4/23/2019 8:00:35 PM",
            "resolvedby": 'null',
            "closeDate": 'null',
            "closedBy": 'null',
            "lastUpdate": 'null',
            "updatedBy": 'null',
            "mostRecentNote": " ",
            "nextScheduledDate": "4/23/2019 4:00:00 AM",
            "flags": "",
            "severity": "100"
        }
        ticket_321 = ticket_123
        ticket_321['ticketID'] = 321
        bruin_client = Mock()
        bruin_client.get_all_tickets = CoroutineMock(side_effect=[
            {'body': [ticket_123, ticket_123], 'status': 200},
            {'body': [ticket_321], 'status': 200}
        ])
        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_ticket_overview(ticket_id)

        assert result == {"body": ticket_123, "status": return_status}

    @pytest.mark.asyncio
    async def get_ticket_overview_none_ticket_id_test(self):
        ticket_id = None

        logger = Mock()

        bruin_client = Mock()
        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_ticket_overview(ticket_id)

        assert result == {'body': 'not ticket id found', 'status': 404}

    @pytest.mark.asyncio
    async def get_ticket_overview_empty_ticket_id_test(self):
        ticket_id = '4503440'
        return_status = 200

        logger = Mock()

        bruin_client = Mock()
        bruin_client.get_all_tickets = CoroutineMock(side_effect=[
            {'body': [], 'status': 200},
        ])
        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_ticket_overview(ticket_id)

        assert result == {"body": [], "status": return_status}

    @pytest.mark.asyncio
    async def get_ticket_overview_4xx_test(self):
        ticket_id = '4503440'
        return_status = 400

        logger = Mock()
        ticket_123 = {
            'ticketID': 123,
            "clientName": "Sam &amp; Su's Retail Shop 5",
            "category": "",
            "topic": "Add Cloud PBX User License",
            "referenceTicketNumber": 0,
            "ticketStatus": "Resolved",
            "address": {
                "address": "69 Blanchard St",
                "city": "Newark",
                "state": "NJ",
                "zip": "07105-4701",
                "country": "USA"
            },
            "createDate": "4/23/2019 7:59:50 PM",
            "createdBy": "Amulya Bidar Nataraj 113",
            "creationNote": 'null',
            "resolveDate": "4/23/2019 8:00:35 PM",
            "resolvedby": 'null',
            "closeDate": 'null',
            "closedBy": 'null',
            "lastUpdate": 'null',
            "updatedBy": 'null',
            "mostRecentNote": " ",
            "nextScheduledDate": "4/23/2019 4:00:00 AM",
            "flags": "",
            "severity": "100"
        }
        ticket_321 = ticket_123
        ticket_321['ticketID'] = 321
        bruin_client = Mock()
        bruin_client.get_all_tickets = CoroutineMock(side_effect=[
            {'body': [ticket_123, ticket_123], 'status': 400},
            {'body': [ticket_321], 'status': 400}
        ])
        bruin_repository = BruinRepository(logger, bruin_client)

        result = await bruin_repository.get_ticket_overview(ticket_id)

        assert result == {"body": [ticket_123, ticket_123], "status": return_status}
