from application.domain.ticket import Ticket, TicketStatus


class TestTicket:
    def proper_status_tickets_are_active_test(self):
        assert Ticket(id=hash("any_id"), status=TicketStatus.NEW).is_active()
        assert Ticket(id=hash("any_id"), status=TicketStatus.IN_PROGRESS).is_active()

    def proper_status_tickets_are_not_active_test(self):
        assert not Ticket(id=hash("any_id"), status=TicketStatus.CLOSED).is_active()
        assert not Ticket(id=hash("any_id"), status=TicketStatus.RESOLVED).is_active()
        assert not Ticket(id=hash("any_id"), status=TicketStatus.DRAFT).is_active()
        assert not Ticket(id=hash("any_id"), status=TicketStatus.IN_REVIEW).is_active()
        assert not Ticket(id=hash("any_id"), status=TicketStatus.UNKNOWN).is_active()

    def empty_status_tickets_are_not_active_test(self):
        assert not Ticket(id=hash("any_id")).is_active()

    def proper_category_tickets_are_repair_tickets_test(self):
        assert Ticket(id=hash("any_id"), category="VOO").is_repair()
        assert Ticket(id=hash("any_id"), category="VAS").is_repair()

    def proper_category_tickets_are_not_repair_tickets_test(self):
        assert not Ticket(id=hash("any_id"), category="019").is_repair()

    def empty_category_tickets_are_not_repair_tickets_test(self):
        assert not Ticket(id=hash("any_id")).is_repair()
