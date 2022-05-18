from unittest.mock import ANY

from application.domain.ticket import Ticket, TicketStatus


class TestTicket:
    def proper_status_tickets_are_active_test(self):
        assert Ticket(id=ANY, status=TicketStatus.NEW).is_active()
        assert Ticket(id=ANY, status=TicketStatus.IN_PROGRESS).is_active()

    def proper_status_tickets_are_not_active_test(self):
        assert not Ticket(id=ANY, status=TicketStatus.CLOSED).is_active()
        assert not Ticket(id=ANY, status=TicketStatus.RESOLVED).is_active()
        assert not Ticket(id=ANY, status=TicketStatus.DRAFT).is_active()
        assert not Ticket(id=ANY, status=TicketStatus.IN_REVIEW).is_active()
        assert not Ticket(id=ANY, status=TicketStatus.UNKNOWN).is_active()

    def empty_status_tickets_are_not_active_test(self):
        assert not Ticket(id=ANY).is_active()

    def proper_category_tickets_are_repair_tickets_test(self):
        assert Ticket(id=ANY, category="VOO").is_repair()
        assert Ticket(id=ANY, category="VAS").is_repair()

    def proper_category_tickets_are_not_repair_tickets_test(self):
        assert not Ticket(id=ANY, category="019").is_repair()

    def empty_category_tickets_are_not_repair_tickets_test(self):
        assert not Ticket(id=ANY).is_repair()
