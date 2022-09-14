import logging
from dataclasses import dataclass

from pydantic import BaseModel

from .nats_client import NatsClient
from .ticket import Ticket

log = logging.getLogger(__name__)

SUBJECT = "bruin.ticket.creation.outage.request"


@dataclass
class TicketRepository:
    nats_client: NatsClient

    async def store(self, ticket: Ticket):
        log.debug(f"store(ticket={ticket})")
        request = Request.build_from(ticket)

        log.debug(f"store:nats_client.request(subject={SUBJECT}, payload={request}, response_body_type=int)")
        response = await self.nats_client.request(SUBJECT, request, int)
        log.debug(f"store:nats_client.request()={response}")


class Request(BaseModel):
    client_id: int
    service_number: int

    @classmethod
    def build_from(cls, ticket: Ticket) -> "Request":
        return cls(client_id=ticket.client_id, service_number=ticket.service_number)
