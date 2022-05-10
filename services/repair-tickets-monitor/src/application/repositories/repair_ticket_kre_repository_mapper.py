from typing import List

from shortuuid import uuid

from application.domain.repair_email_output import RepairEmailOutput, TicketOutput
from application.domain.ticket import Ticket


def to_output_message(output: RepairEmailOutput):
    body = {
        "email_id": str(output.email_id),
        "service_numbers_sites_map": output.service_numbers_sites_map,
        "tickets_created": to_ticket_list(output.tickets_created),
        "tickets_updated": to_ticket_list(output.tickets_updated),
        "tickets_could_be_created": to_ticket_list(output.tickets_could_be_created),
        "tickets_could_be_updated": to_ticket_list(output.tickets_could_be_updated),
        "tickets_cannot_be_created": to_ticket_list(output.tickets_cannot_be_created),
        "validated_tickets": to_validated_ticket_list(output.validated_tickets),
    }
    compressed_body = {k: v for k, v in body.items() if v}

    return {
        "request_id": uuid(),
        "body": compressed_body,
    }


def to_ticket_list(ticket_outputs: List[TicketOutput]):
    return [to_ticket(ticket_output) for ticket_output in ticket_outputs]


def to_ticket(ticket_output: TicketOutput):
    ticket = {
        "site_id": str(ticket_output.site_id) if ticket_output.site_id else None,
        "service_numbers": ticket_output.service_numbers,
        "ticket_id": str(ticket_output.ticket_id) if ticket_output.ticket_id else None,
        "not_creation_reason": ticket_output.reason,
    }

    return {k: v for k, v in ticket.items() if v}


def to_validated_ticket_list(tickets: List[Ticket]):
    return [to_validated_ticket(ticket) for ticket in tickets]


def to_validated_ticket(ticket: Ticket):
    validated_ticket = {
        "ticket_id": str(ticket.id),
        "site_id": str(ticket.site_id) if ticket.site_id else None,
        "ticket_status": ticket.status.value if ticket.status else None,
        "call_type": ticket.call_type,
        "category": ticket.category,
    }

    return {k: v for k, v in validated_ticket.items() if v}
