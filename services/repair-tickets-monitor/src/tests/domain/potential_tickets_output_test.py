from application.domain.potential_tickets_output import PotentialTicketsOutput


class PotentialTicketsOutputTest:
    def instance_test(self):
        potential_tickets_output = PotentialTicketsOutput()

        assert potential_tickets_output.tickets_could_be_created == []
        assert potential_tickets_output.tickets_could_be_updated == []
