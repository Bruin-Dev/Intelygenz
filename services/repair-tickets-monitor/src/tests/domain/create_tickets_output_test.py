from application.domain.create_tickets_output import CreateTicketsOutput


class TestCreateTicketsOutput:
    def instance_test(self):
        create_tickets_output = CreateTicketsOutput()

        assert create_tickets_output.tickets_created == []
        assert create_tickets_output.tickets_updated == []
        assert create_tickets_output.tickets_cannot_be_created == []
