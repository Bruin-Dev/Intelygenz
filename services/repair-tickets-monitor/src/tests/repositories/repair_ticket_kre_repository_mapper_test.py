import pytest
from pytest_lazyfixture import lazy_fixture

from application.domain.repair_email_output import RepairEmailOutput
from application.domain.ticket_output import TicketOutput
from application.repositories.repair_ticket_kre_repository_mapper import to_output_message, to_output_ticket_message


@pytest.fixture()
def a_ticket_output():
    return TicketOutput(
        site_id="site_id",
        ticket_id="ticket_id",
        ticket_status="status",
        reason="reason",
        category="category",
        call_type="call_type",
        service_numbers=["sn_1", "sn_2"],
    )


@pytest.fixture()
def a_ticket_output_message():
    return {
        "site_id": "site_id",
        "ticket_id": "ticket_id",
        "ticket_status": "status",
        "not_creation_reason": "reason",
        "category": "category",
        "call_type": "call_type",
        "service_numbers": ["sn_1", "sn_2"],
    }


@pytest.fixture()
def a_repair_email_output(a_ticket_output):
    return RepairEmailOutput(
        email_id="email_id",
        service_numbers_sites_map={"sn_1": "site_1", "sn_2": "site_1"},
        validated_ticket_numbers=["ticket_1", "ticket_2"],
        tickets_created=[a_ticket_output],
        tickets_updated=[a_ticket_output],
        tickets_could_be_created=[a_ticket_output],
        tickets_could_be_updated=[a_ticket_output],
        tickets_cannot_be_created=[a_ticket_output],
    )


@pytest.fixture()
def a_repair_email_output_message(a_ticket_output_message):
    return {
        "email_id": "email_id",
        "service_numbers_sites_map": {"sn_1": "site_1", "sn_2": "site_1"},
        "validated_ticket_numbers": ["ticket_1", "ticket_2"],
        "validated_service_numbers": ["sn_1", "sn_2"],
        "tickets_created": [a_ticket_output_message],
        "tickets_updated": [a_ticket_output_message],
        "tickets_could_be_created": [a_ticket_output_message],
        "tickets_could_be_updated": [a_ticket_output_message],
        "tickets_cannot_be_created": [a_ticket_output_message],
    }


class TestRepairTicketKreRepositoryMapper:
    @pytest.mark.parametrize(
        "repair_email_output, expected_body",
        [
            (RepairEmailOutput(email_id="1234"), {"email_id": "1234"}),
            (lazy_fixture("a_repair_email_output"), lazy_fixture("a_repair_email_output_message"))
        ]
    )
    def to_output_message_test(self, repair_email_output, expected_body):
        output_message = to_output_message(repair_email_output)
        assert output_message["request_id"]
        assert output_message["body"] == expected_body

    @pytest.mark.parametrize(
        "ticket_output, expected_message",
        [
            (TicketOutput(), {}),
            (lazy_fixture("a_ticket_output"), lazy_fixture("a_ticket_output_message")),
        ],
    )
    def to_output_ticket_message_test(self, ticket_output, expected_message):
        assert to_output_ticket_message(ticket_output) == expected_message
