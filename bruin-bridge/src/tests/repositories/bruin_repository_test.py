from unittest.mock import call
from unittest.mock import Mock

from application.repositories.bruin_repository import BruinRepository


class TestBruinRepository:

    def instance_test(self):
        logger = Mock()
        bruin_client = Mock()

        bruin_repository = BruinRepository(logger, bruin_client)

        assert bruin_repository._logger is logger
        assert bruin_repository._bruin_client is bruin_client

    def get_all_filtered_tickets_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = Mock(side_effect=[
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
        filtered_tickets = bruin_repository.get_all_filtered_tickets(
            params=params,
            ticket_status=[ticket_status_1, ticket_status_2],
        )

        bruin_repository._bruin_client.get_all_tickets.assert_has_calls([
            call(full_params_1),
            call(full_params_2),
        ], any_order=False)
        assert filtered_tickets['body'] == [{'ticketID': 123}, {'ticketID': 321}]
        assert filtered_tickets['status'] == 200

    def get_all_filtered_tickets_with_none_returned_for_one_ticket_status_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = Mock(side_effect=[
            {'body': [{'ticketID': 123}, {'ticketID': 321}], 'status': 200},
            {'body': None, 'status': 404},
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
        filtered_tickets = bruin_repository.get_all_filtered_tickets(
            params=params,
            ticket_status=[ticket_status_1, ticket_status_2, ticket_status_3]
        )

        bruin_repository._bruin_client.get_all_tickets.assert_has_calls([
            call(full_params_1),
            call(full_params_2),
        ], any_order=False)
        assert call(full_params_3) not in bruin_repository._bruin_client.get_all_tickets.mock_calls
        assert filtered_tickets['body'] is None
        assert filtered_tickets['status'] == 404

    def get_filtered_tickets_with_bruin_returning_empty_lists_for_every_status_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = Mock(side_effect=[
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
        filtered_tickets = bruin_repository.get_all_filtered_tickets(
            params=params,
            ticket_status=[ticket_status_1, ticket_status_2],
            )

        bruin_repository._bruin_client.get_all_tickets.assert_has_calls([
            call(full_params_1),
            call(full_params_2)
        ], any_order=True)
        assert filtered_tickets['body'] == []
        assert filtered_tickets['status'] == 200

    def get_ticket_details_test(self):
        logger = Mock()
        ticket_id = 123
        expected_ticket_details = 'Some Ticket Details'

        bruin_client = Mock()
        bruin_client.get_ticket_details = Mock(return_value=expected_ticket_details)

        bruin_repository = BruinRepository(logger, bruin_client)
        ticket_details = bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._bruin_client.get_ticket_details.assert_called_once_with(ticket_id)
        assert ticket_details == expected_ticket_details

    def get_ticket_details_by_edge_serial_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'
        params = dict(client_id=123, category='SD-WAN', ticket_topic='VAS')
        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]

        ticket_1_id = 123
        ticket_2_id = 321
        ticket_3_id = 456

        ticket_1_details = {
            'ticketDetails': [
                {
                    "detailID": 2746999,
                    "detailValue": 'This is a meaningless detail',
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894999,
                    "noteValue": 'Nothing to do here!',
                }
            ],
        }
        ticket_2_details = {
            'ticketDetails': [
                {
                    "detailID": 2746937,
                    "detailValue": edge_serial,
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894041,
                    "noteValue": f'#*Automation Engine*# \n TimeStamp: 2019-07-30 06:38:00+00:00',
                }
            ],
        }
        ticket_3_details = {
            'ticketDetails': [
                {
                    "detailID": 2741000,
                    "detailValue": edge_serial,
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41891000,
                    "noteValue": 'Nothing to do here!',
                }
            ],
        }

        bruin_repository = BruinRepository(logger, bruin_client)
        bruin_repository.get_all_filtered_tickets = Mock(return_value={'body': [
            {'ticketID': ticket_1_id},
            {'ticketID': ticket_2_id},
            {'ticketID': ticket_3_id},
        ], 'status': 200})
        bruin_repository.get_ticket_details = Mock(side_effect=[
            {'body': ticket_1_details, 'status': 200}, {'body': ticket_2_details, 'status': 200},
            {'body': ticket_3_details, 'status': 200}])

        ticket_details_by_edge = bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, params=params,
            ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_all_filtered_tickets.assert_called_once_with(
            params=params,
            ticket_status=ticket_statuses,

        )
        bruin_repository.get_ticket_details.assert_has_calls([
            call(ticket_1_id), call(ticket_2_id), call(ticket_3_id),
        ], any_order=False)

        expected_ticket_details_list = [
            {
                'ticketID': ticket_2_id,
                **ticket_2_details,
            },
            {
                'ticketID': ticket_3_id,
                **ticket_3_details,
            },
        ]
        assert ticket_details_by_edge['body'] == expected_ticket_details_list
        assert ticket_details_by_edge['status'] == 200

    def get_ticket_details_by_edge_serial_with_no_filtered_tickets_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'
        params = dict(client_id=123, category='SD-WAN', ticket_topic='VAS')
        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]

        bruin_repository = BruinRepository(logger, bruin_client)
        bruin_repository.get_all_filtered_tickets = Mock(return_value={"body": [], "status": 200})
        bruin_repository.get_ticket_details = Mock()

        ticket_details_by_edge = bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, params=params,
            ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_all_filtered_tickets.assert_called_once_with(
            ticket_status=ticket_statuses,
            params=params
        )
        bruin_repository.get_ticket_details.assert_not_called()

        expected_ticket_details_list = []
        assert ticket_details_by_edge["body"] == expected_ticket_details_list
        assert ticket_details_by_edge['status'] == 200

    def get_ticket_details_by_edge_serial_with_filtered_tickets_and_no_ticket_details_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'

        params = dict(client_id=123, category='SD-WAN', ticket_topic='VAS'
                      )
        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]

        ticket_1_id = 123
        ticket_2_id = 321
        ticket_3_id = 456

        ticket_1_details = {
            'ticketDetails': [],
            'ticketNotes': [],
        }
        ticket_2_details = {
            'ticketDetails': [],
            'ticketNotes': [],
        }
        ticket_3_details = {
            'ticketDetails': [],
            'ticketNotes': [],
        }

        bruin_repository = BruinRepository(logger, bruin_client)
        bruin_repository.get_all_filtered_tickets = Mock(return_value={"body": [
            {'ticketID': ticket_1_id},
            {'ticketID': ticket_2_id},
            {'ticketID': ticket_3_id},
        ], "status": 200})
        bruin_repository.get_ticket_details = Mock(side_effect=[
            {"body": ticket_1_details, "status": 200},
            {"body": ticket_2_details, "status": 200},
            {"body": ticket_3_details, "status": 200},
        ])

        ticket_details_by_edge = bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, params=params,
            ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_all_filtered_tickets.assert_called_once_with(
            params=params,
            ticket_status=ticket_statuses,
        )
        bruin_repository.get_ticket_details.assert_has_calls([
            call(ticket_1_id), call(ticket_2_id), call(ticket_3_id)
        ], any_order=True)

        expected_ticket_details_list = []
        assert ticket_details_by_edge["body"] == expected_ticket_details_list
        assert ticket_details_by_edge['status'] == 200

    def get_ticket_details_by_edge_serial_with_filtered_tickets_and_ticket_details_and_no_serial_coincidence_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'

        params = dict(client_id=123, category='SD-WAN', ticket_topic='VAS')

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]

        ticket_1_id = 123
        ticket_2_id = 321
        ticket_3_id = 456

        ticket_1_details = {
            'ticketDetails': [
                {
                    "detailID": 2746999,
                    "detailValue": 'This is a meaningless detail',
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894999,
                    "noteValue": 'Nothing to do here!',
                }
            ],
        }
        ticket_2_details = {
            'ticketDetails': [
                {
                    "detailID": 2746937,
                    "detailValue": 'Nothing to do here!',
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894041,
                    "noteValue": 'This is a meaningless detail',
                }
            ],
        }
        ticket_3_details = {
            'ticketDetails': [
                {
                    "detailID": 2741000,
                    "detailValue": 'This is a meaningless detail',
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41891000,
                    "noteValue": 'Nothing to do here!',
                }
            ],
        }

        bruin_repository = BruinRepository(logger, bruin_client)
        bruin_repository.get_all_filtered_tickets = Mock(return_value={"body": [
            {'ticketID': ticket_1_id},
            {'ticketID': ticket_2_id},
            {'ticketID': ticket_3_id},
        ], "status": 200})
        bruin_repository.get_ticket_details = Mock(side_effect=[
            {"body": ticket_1_details, "status": 200},
            {"body": ticket_2_details, "status": 200},
            {"body": ticket_3_details, "status": 200},
        ])

        ticket_details_by_edge = bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, params=params,
            ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_all_filtered_tickets.assert_called_once_with(
            params=params,
            ticket_status=ticket_statuses,
        )
        bruin_repository.get_ticket_details.assert_has_calls([
            call(ticket_1_id), call(ticket_2_id), call(ticket_3_id)
        ], any_order=False)

        expected_ticket_details_list = []
        assert ticket_details_by_edge["body"] == expected_ticket_details_list
        assert ticket_details_by_edge['status'] == 200

    def get_affecting_ticket_details_by_edge_serial_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'
        client_id = 123

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]
        category = 'SD-WAN'
        ticket_topic = 'VAS'

        ticket_id = 123
        ticket_details = [{
            'ticketID': ticket_id,
            'ticketDetails': [
                {
                    "detailID": 2746999,
                    "detailValue": 'This is a meaningless detail',
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894999,
                    "noteValue": 'Nothing to do here!',
                }
            ],
        }]

        bruin_repository = BruinRepository(logger, bruin_client)
        bruin_repository.get_ticket_details_by_edge_serial = Mock(return_value=dict(body=ticket_details,
                                                                                    status=200))

        affecting_ticket_details_by_edge = bruin_repository.get_affecting_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
            category=category, ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_ticket_details_by_edge_serial.assert_called_once_with(
            edge_serial=edge_serial,
            params=dict(
                ticket_topic=ticket_topic,
                client_id=client_id,
                category=category),
            ticket_statuses=ticket_statuses,
        )
        assert affecting_ticket_details_by_edge["body"] == ticket_details
        assert affecting_ticket_details_by_edge["status"] == 200

    def get_outage_ticket_details_by_edge_serial_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'
        client_id = 123

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]
        category = 'SD-WAN'
        ticket_topic = 'VOO'

        ticket_id = 123
        ticket_details = {
            'ticketID': ticket_id,
            'ticketDetails': [
                {
                    "detailID": 2746999,
                    "detailValue": 'This is a meaningless detail',
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894999,
                    "noteValue": 'Nothing to do here!',
                }
            ],
        }

        bruin_repository = BruinRepository(logger, bruin_client)
        bruin_repository.get_ticket_details_by_edge_serial = Mock(return_value=dict(body=[ticket_details],
                                                                                    status=200))

        outage_ticket_details_by_edge = bruin_repository.get_outage_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
            category=category, ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_ticket_details_by_edge_serial.assert_called_once_with(
            edge_serial=edge_serial,
            params=dict(
                ticket_topic=ticket_topic,
                client_id=client_id,
                category=category),
            ticket_statuses=ticket_statuses,
        )
        assert outage_ticket_details_by_edge["body"] == ticket_details
        assert outage_ticket_details_by_edge["status"] == 200

    def get_outage_ticket_details_by_edge_serial_empty_return_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'
        client_id = 123

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]
        category = 'SD-WAN'
        ticket_topic = 'VOO'

        ticket_id = 123
        ticket_details = {
            'ticketID': ticket_id,
            'ticketDetails': [
                {
                    "detailID": 2746999,
                    "detailValue": 'This is a meaningless detail',
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894999,
                    "noteValue": 'Nothing to do here!',
                }
            ],
        }

        bruin_repository = BruinRepository(logger, bruin_client)
        bruin_repository.get_ticket_details_by_edge_serial = Mock(return_value=dict(body=[],
                                                                                    status=200))

        outage_ticket_details_by_edge = bruin_repository.get_outage_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
            category=category, ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_ticket_details_by_edge_serial.assert_called_once_with(
            edge_serial=edge_serial,
            params=dict(
                ticket_topic=ticket_topic,
                client_id=client_id,
                category=category),
            ticket_statuses=ticket_statuses,
        )
        assert outage_ticket_details_by_edge["body"] == []
        assert outage_ticket_details_by_edge["status"] == 200

    def post_ticket_note_test(self):
        logger = Mock()
        ticket_id = 123
        note_contents = 'TicketNote'
        payload = dict(note=note_contents)
        expected_post_response = 'Ticket Appended'

        bruin_client = Mock()
        bruin_client.post_ticket_note = Mock(return_value=expected_post_response)

        bruin_repository = BruinRepository(logger, bruin_client)
        post_response = bruin_repository.post_ticket_note(ticket_id, note_contents)

        bruin_client.post_ticket_note.assert_called_once_with(ticket_id, payload)
        assert post_response == expected_post_response

    def post_ticket_test(self):
        logger = Mock()
        payload = dict(client_id=321, category='Some Category', notes=['List of Notes'],
                       services=['List of Services'], contacts=['List of Contacts'])
        expected_post_response = 'Ticket Created'

        bruin_client = Mock()
        bruin_client.post_ticket = Mock(return_value=expected_post_response)

        bruin_repository = BruinRepository(logger, bruin_client)
        create_ticket = bruin_repository.post_ticket(payload)
        bruin_client.post_ticket.assert_called_once_with(payload)
        assert create_ticket == expected_post_response

    def open_ticket_test(self):
        logger = Mock()

        ticket_id = 123
        detail_id = 321
        payload = dict(Status='O')
        successful_status_change = 'Success'

        bruin_client = Mock()
        bruin_client.update_ticket_status = Mock(return_value=successful_status_change)

        bruin_repository = BruinRepository(logger, bruin_client)
        change_status = bruin_repository.open_ticket(ticket_id, detail_id)
        bruin_client.update_ticket_status.assert_called_once_with(ticket_id, detail_id, payload)
        assert change_status == successful_status_change

    def resolve_ticket_test(self):
        logger = Mock()

        ticket_id = 123
        detail_id = 321
        payload = dict(Status='R')
        successful_status_change = 'Success'

        bruin_client = Mock()
        bruin_client.update_ticket_status = Mock(return_value=successful_status_change)

        bruin_repository = BruinRepository(logger, bruin_client)
        change_status = bruin_repository.resolve_ticket(ticket_id, detail_id)
        bruin_client.update_ticket_status.assert_called_once_with(ticket_id, detail_id, payload)
        assert change_status == successful_status_change

    def get_management_status_ok_test(self):
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
        bruin_client.get_management_status = Mock(return_value=response)
        bruin_repository = BruinRepository(logger, bruin_client)
        response = bruin_repository.get_management_status(filters)
        management_status = response["body"]
        bruin_client.get_management_status.assert_called_once_with(filters)
        assert "Active – Platinum Monitoring" in management_status

    def get_management_status_400_test(self):
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
        bruin_client.get_management_status = Mock(return_value=response)
        bruin_repository = BruinRepository(logger, bruin_client)
        management_status = bruin_repository.get_management_status(filters)
        bruin_client.get_management_status.assert_called_once_with(filters)
        assert management_status == response

    def get_management_status_ko_test(self):
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
        bruin_client.get_management_status = Mock(return_value=response)
        bruin_repository = BruinRepository(logger, bruin_client)
        management_status = bruin_repository.get_management_status(filters)
        bruin_client.get_management_status.assert_called_once_with(filters)
        assert management_status == response

    def post_outage_ticket_with_2XX_status_code_test(self):
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
            "status_code": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = Mock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_called_once_with(client_id, service_number)
        assert result == {"body": ticket_id, "status_code": response_status}

    def post_outage_ticket_with_409_status_code_test(self):
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
            "status_code": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = Mock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_called_once_with(client_id, service_number)
        assert result == {"body": ticket_id, "status_code": response_status}

    def post_outage_ticket_with_471_status_code_test(self):
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
            "status_code": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = Mock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_called_once_with(client_id, service_number)
        assert result == {"body": ticket_id, "status_code": response_status}

    def post_outage_ticket_with_error_status_code_test(self):
        client_id = 9994
        service_number = "VC05400002265"

        response_status = 500
        client_response = {
            "body": "Got internal error from Bruin",
            "status_code": response_status,
        }

        logger = Mock()

        bruin_client = Mock()
        bruin_client.post_outage_ticket = Mock(return_value=client_response)

        bruin_repository = BruinRepository(logger, bruin_client)

        result = bruin_repository.post_outage_ticket(client_id, service_number)

        bruin_client.post_outage_ticket.assert_called_once_with(client_id, service_number)
        assert result == client_response
