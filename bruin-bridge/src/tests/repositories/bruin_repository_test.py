from unittest.mock import Mock

from application.repositories.bruin_repository import BruinRepository


class TestBruinRepository:

    def instance_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_repository = BruinRepository(logger, bruin_client)
        assert bruin_repository._logger is logger
        assert bruin_repository._bruin_client is bruin_client

    def get_filtered_tickets_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_all_tickets = Mock(return_value='All Tickets')
        bruin_repository = BruinRepository(logger, bruin_client)
        filtered_tickets = bruin_repository.get_all_filtered_tickets(123, 321, ["New", "In-Progress"], "SD-WAN")
        assert bruin_client.get_all_tickets.called
        assert bruin_client.get_all_tickets.call_args[0][0] == 123
        assert bruin_client.get_all_tickets.call_args[0][1] == 321
        assert bruin_client.get_all_tickets.call_args[0][2] == ["New", "In-Progress"]
        assert bruin_client.get_all_tickets.call_args[0][3] == "SD-WAN"
        assert filtered_tickets == 'All Tickets'

    def get_ticket_details_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.get_ticket_details = Mock(return_value='Some Ticket Details')
        bruin_repository = BruinRepository(logger, bruin_client)
        ticket_details = bruin_repository.get_ticket_details(123)
        assert bruin_client.get_ticket_details.called
        assert bruin_client.get_ticket_details.call_args[0][0] == 123
        assert ticket_details == 'Some Ticket Details'

    def post_ticket_note_test(self):
        logger = Mock()
        bruin_client = Mock()
        bruin_client.post_ticket_note = Mock(return_value='Ticket Appended')
        bruin_repository = BruinRepository(logger, bruin_client)
        appened_ticket = bruin_repository.post_ticket_note(123, 'TicketNote')
        assert bruin_client.post_ticket_note.called
        assert bruin_client.post_ticket_note.call_args[0][0] == 123
        assert bruin_client.post_ticket_note.call_args[0][1] == 'TicketNote'
        assert appened_ticket == 'Ticket Appended'
