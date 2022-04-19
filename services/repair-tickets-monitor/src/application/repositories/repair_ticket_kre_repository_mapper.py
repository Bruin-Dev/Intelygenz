from typing import List

from shortuuid import uuid

from application.domain.repair_email_output import RepairEmailOutput
from application.domain.ticket_output import TicketOutput


def to_output_message(output: RepairEmailOutput):
    validated_service_numbers = (
        list(output.service_numbers_sites_map.keys())
        if output.service_numbers_sites_map
        else [])

    body = {
        "email_id": output.email_id,
        "validated_service_numbers": validated_service_numbers,
        "validated_ticket_numbers": output.validated_ticket_numbers,
        "service_numbers_sites_map": output.service_numbers_sites_map,
        "tickets_created": to_output_message_list(output.tickets_created),
        "tickets_updated": to_output_message_list(output.tickets_updated),
        "tickets_could_be_created": to_output_message_list(output.tickets_could_be_created),
        "tickets_could_be_updated": to_output_message_list(output.tickets_could_be_updated),
        "tickets_cannot_be_created": to_output_message_list(output.tickets_cannot_be_created),
    }
    compressed_body = {k: v for k, v in body.items() if v}

    return {
        "request_id": uuid(),
        "body": compressed_body,
    }


def to_output_message_list(ticket_output_list: List[TicketOutput]):
    return [to_output_ticket_message(ticket_output) for ticket_output in ticket_output_list]


def to_output_ticket_message(ticket_output: TicketOutput):
    ticket_message = {
        "site_id": ticket_output.site_id,
        "service_numbers": ticket_output.service_numbers,
        "ticket_id": ticket_output.ticket_id,
        "not_creation_reason": ticket_output.reason,
        "ticket_status": ticket_output.ticket_status,
        "category": ticket_output.category,
        "call_type": ticket_output.call_type
    }

    return {k: v for k, v in ticket_message.items() if v}
