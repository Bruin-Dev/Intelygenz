from application.domain.repair_email_output import RepairEmailOutput, TicketOutput
from application.domain.ticket import Ticket, TicketStatus
from application.repositories.repair_ticket_kre_repository_mapper import to_output_message


class TestRepairTicketKreRepositoryMapper:
    def mandatory_output_fields_are_properly_mapped_test(self):
        repair_email_output = RepairEmailOutput(email_id=hash("any_email_id"))
        output_message = to_output_message(repair_email_output)
        assert output_message["request_id"]
        assert output_message["body"] == {"email_id": str(hash("any_email_id"))}

    def mandatory_validated_ticket_fields_are_properly_mapped_test(self):
        repair_email_output = RepairEmailOutput(
            email_id=hash("any_email_id"),
            validated_tickets=[Ticket(id=hash("any_ticket_id"))]
        )
        output_message = to_output_message(repair_email_output)
        assert output_message["request_id"]
        assert output_message["body"] == {
            "email_id": str(hash("any_email_id")),
            "validated_tickets": [{
                "ticket_id": str(hash("any_ticket_id"))
            }]
        }

    def all_fields_are_properly_mapped_test(self):
        any_ticket_output = TicketOutput(
            site_id="any_ticket_output_site_id",
            ticket_id=hash("any_ticket_output_id"),
            reason="any_reason",
            service_numbers=["any_service_number"]
        )
        any_ticket = Ticket(
            id=hash("any_ticket_id"),
            site_id=hash("any_ticket_site_id"),
            status=TicketStatus.NEW,
            call_type="any_call_type",
            category="any_category"
        )
        repair_email_output = RepairEmailOutput(
            email_id=hash("any_email_id"),
            service_numbers_sites_map={"any_service_number": "any_site"},
            tickets_created=[any_ticket_output],
            tickets_updated=[any_ticket_output],
            tickets_could_be_created=[any_ticket_output],
            tickets_could_be_updated=[any_ticket_output],
            tickets_cannot_be_created=[any_ticket_output],
            validated_tickets=[any_ticket]
        )

        subject = to_output_message(repair_email_output)

        expected_ticket = {
            "ticket_id": str(hash("any_ticket_output_id")),
            "site_id": "any_ticket_output_site_id",
            "not_creation_reason": "any_reason",
            "service_numbers": ["any_service_number"]
        }
        assert subject["request_id"]
        assert subject["body"] == {
            "email_id": str(hash("any_email_id")),
            "service_numbers_sites_map": {"any_service_number": "any_site"},
            "tickets_created": [expected_ticket],
            "tickets_updated": [expected_ticket],
            "tickets_could_be_created": [expected_ticket],
            "tickets_could_be_updated": [expected_ticket],
            "tickets_cannot_be_created": [expected_ticket],
            "validated_tickets": [{
                "ticket_id": str(hash("any_ticket_id")),
                "site_id": str(hash("any_ticket_site_id")),
                "ticket_status": "New",
                "call_type": "any_call_type",
                "category": "any_category"
            }],
        }
