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
            [{'ticketID': 123}, {'ticketID': 123}],
            [{'ticketID': 321}],
        ])
        client_id = 123
        ticket_id = 321
        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        category = 'SD-WAN'
        ticket_topic = 'VOO'

        bruin_repository = BruinRepository(logger, bruin_client)
        filtered_tickets = bruin_repository.get_all_filtered_tickets(
            client_id=client_id, ticket_id=ticket_id,
            ticket_status=[ticket_status_1, ticket_status_2],
            category=category, ticket_topic=ticket_topic
        )

        bruin_repository._bruin_client.get_all_tickets.assert_has_calls([
            call(client_id, ticket_id, ticket_status_1, category, ticket_topic),
            call(client_id, ticket_id, ticket_status_2, category, ticket_topic),
        ], any_order=True)
        assert filtered_tickets == [{'ticketID': 123}, {'ticketID': 321}]

    def get_all_filtered_tickets_with_none_returned_for_one_ticket_status_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = Mock(side_effect=[
            [{'ticketID': 123}, {'ticketID': 321}],
            None,
        ])
        client_id = 123
        ticket_id = 321
        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_status_3 = "Yet-Another-Status"
        category = 'SD-WAN'
        ticket_topic = 'VOO'

        bruin_repository = BruinRepository(logger, bruin_client)
        filtered_tickets = bruin_repository.get_all_filtered_tickets(
            client_id=client_id, ticket_id=ticket_id,
            ticket_status=[ticket_status_1, ticket_status_2, ticket_status_3],
            category=category, ticket_topic=ticket_topic
        )

        bruin_repository._bruin_client.get_all_tickets.assert_has_calls([
            call(client_id, ticket_id, ticket_status_1, category, ticket_topic),
            call(client_id, ticket_id, ticket_status_2, category, ticket_topic),
        ], any_order=False)
        assert call(client_id, ticket_id, ticket_status_3, category) not in \
            bruin_repository._bruin_client.get_all_tickets.mock_calls
        assert filtered_tickets is None

    def get_filtered_tickets_with_bruin_returning_empty_lists_for_every_status_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = Mock(side_effect=[
            [],
            [],
        ])
        client_id = 123
        ticket_id = 321
        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        category = 'SD-WAN'
        ticket_topic = 'VOO'

        bruin_repository = BruinRepository(logger, bruin_client)
        filtered_tickets = bruin_repository.get_all_filtered_tickets(
            client_id=client_id, ticket_id=ticket_id,
            ticket_status=[ticket_status_1, ticket_status_2],
            category=category, ticket_topic=ticket_topic
        )

        bruin_repository._bruin_client.get_all_tickets.assert_has_calls([
            call(client_id, ticket_id, ticket_status_1, category, ticket_topic),
            call(client_id, ticket_id, ticket_status_2, category, ticket_topic),
        ], any_order=True)
        assert filtered_tickets == []

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
        client_id = 123

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]
        category = 'SD-WAN'
        ticket_topic = 'VOO'

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
        bruin_repository.get_all_filtered_tickets = Mock(return_value=[
            {'ticketID': ticket_1_id},
            {'ticketID': ticket_2_id},
            {'ticketID': ticket_3_id},
        ])
        bruin_repository.get_ticket_details = Mock(side_effect=[
            ticket_1_details, ticket_2_details, ticket_3_details,
        ])

        ticket_details_by_edge = bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
            category=category, ticket_topic=ticket_topic,
            ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_all_filtered_tickets.assert_called_once_with(
            client_id=client_id,
            ticket_id=None,
            ticket_status=ticket_statuses,
            category=category,
            ticket_topic=ticket_topic
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
        assert ticket_details_by_edge == expected_ticket_details_list

    def get_ticket_details_by_edge_serial_with_no_filtered_tickets_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'
        client_id = 123

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]
        category = 'SD-WAN'
        ticket_topic = 'VOO'

        bruin_repository = BruinRepository(logger, bruin_client)
        bruin_repository.get_all_filtered_tickets = Mock(return_value=[])
        bruin_repository.get_ticket_details = Mock()

        ticket_details_by_edge = bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
            category=category, ticket_topic=ticket_topic,
            ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_all_filtered_tickets.assert_called_once_with(
            client_id=client_id,
            ticket_id=None,
            ticket_status=ticket_statuses,
            category=category,
            ticket_topic=ticket_topic
        )
        bruin_repository.get_ticket_details.assert_not_called()

        expected_ticket_details_list = []
        assert ticket_details_by_edge == expected_ticket_details_list

    def get_ticket_details_by_edge_serial_with_filtered_tickets_and_no_ticket_details_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'
        client_id = 123

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]
        category = 'SD-WAN'
        ticket_topic = 'VOO'

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
        bruin_repository.get_all_filtered_tickets = Mock(return_value=[
            {'ticketID': ticket_1_id},
            {'ticketID': ticket_2_id},
            {'ticketID': ticket_3_id},
        ])
        bruin_repository.get_ticket_details = Mock(side_effect=[
            ticket_1_details, ticket_2_details, ticket_3_details,
        ])

        ticket_details_by_edge = bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
            category=category, ticket_topic=ticket_topic,
            ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_all_filtered_tickets.assert_called_once_with(
            client_id=client_id,
            ticket_id=None,
            ticket_status=ticket_statuses,
            category=category,
            ticket_topic=ticket_topic
        )
        bruin_repository.get_ticket_details.assert_has_calls([
            call(ticket_1_id), call(ticket_2_id), call(ticket_3_id)
        ], any_order=True)

        expected_ticket_details_list = []
        assert ticket_details_by_edge == expected_ticket_details_list

    def get_ticket_details_by_edge_serial_with_filtered_tickets_and_ticket_details_and_no_serial_coincidence_test(self):
        logger = Mock()
        bruin_client = Mock()

        edge_serial = 'VC05200026138'
        client_id = 123

        ticket_status_1 = "New"
        ticket_status_2 = "In-Progress"
        ticket_statuses = [ticket_status_1, ticket_status_2]
        category = 'SD-WAN'
        ticket_topic = 'VOO'

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
        bruin_repository.get_all_filtered_tickets = Mock(return_value=[
            {'ticketID': ticket_1_id},
            {'ticketID': ticket_2_id},
            {'ticketID': ticket_3_id},
        ])
        bruin_repository.get_ticket_details = Mock(side_effect=[
            ticket_1_details, ticket_2_details, ticket_3_details,
        ])

        ticket_details_by_edge = bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
            category=category, ticket_topic=ticket_topic,
            ticket_statuses=ticket_statuses,
        )

        bruin_repository.get_all_filtered_tickets.assert_called_once_with(
            client_id=client_id,
            ticket_id=None,
            ticket_status=ticket_statuses,
            category=category,
            ticket_topic=ticket_topic
        )
        bruin_repository.get_ticket_details.assert_has_calls([
            call(ticket_1_id), call(ticket_2_id), call(ticket_3_id)
        ], any_order=False)

        expected_ticket_details_list = []
        assert ticket_details_by_edge == expected_ticket_details_list

    def post_ticket_note_test(self):
        logger = Mock()
        ticket_id = 123
        note_contents = 'TicketNote'
        expected_post_response = 'Ticket Appended'

        bruin_client = Mock()
        bruin_client.post_ticket_note = Mock(return_value=expected_post_response)

        bruin_repository = BruinRepository(logger, bruin_client)
        post_response = bruin_repository.post_ticket_note(ticket_id, note_contents)

        bruin_client.post_ticket_note.assert_called_once_with(ticket_id, note_contents)
        assert post_response == expected_post_response

    def post_ticket_test(self):
        logger = Mock()
        client_id = 321
        category = 'Some Category'
        notes = ['List of Notes']
        services = ['List of Services']
        contacts = ['List of Contacts']
        expected_post_response = 'Ticket Created'

        bruin_client = Mock()
        bruin_client.post_ticket = Mock(return_value=expected_post_response)

        bruin_repository = BruinRepository(logger, bruin_client)
        create_ticket = bruin_repository.post_ticket(client_id, category, services, notes, contacts)
        bruin_client.post_ticket.assert_called_once_with(client_id, category, services, notes, contacts)
        assert create_ticket == expected_post_response
