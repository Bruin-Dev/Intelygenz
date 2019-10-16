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
        bruin_client = Mock()
        bruin_client.post_ticket = Mock(return_value='Ticket Created')
        bruin_repository = BruinRepository(logger, bruin_client)
        create_ticket = bruin_repository.post_ticket(123, 'Some Category', ['Services'], ['Notes'], ['Contacts'])
        assert bruin_client.post_ticket.called
        assert bruin_client.post_ticket.call_args[0][0] == 123
        assert bruin_client.post_ticket.call_args[0][1] == 'Some Category'
        assert bruin_client.post_ticket.call_args[0][2] == ['Services']
        assert bruin_client.post_ticket.call_args[0][3] == ['Notes']
        assert bruin_client.post_ticket.call_args[0][4] == ['Contacts']
        assert create_ticket == 'Ticket Created'
