import logging
from dataclasses import dataclass

from pydantic import BaseModel, BaseSettings

from .nats_client import NatsClient
from .ticket import Ticket

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    subject: str = "bruin.ticket.creation.outage.request"


@dataclass
class TicketRepository:
    settings: Settings
    nats_client: NatsClient

    async def store(self, ticket: Ticket):
        log.debug(f"store(ticket={ticket})")
        request = to_request(ticket)

        response = await self.nats_client.request(self.settings.subject, request)
        log.debug(f"store:nats_client.request()={response}")


def to_request(ticket: Ticket):
    log.debug(f"to_request(ticket={ticket}")
    return Request(client_id=ticket.client_id, service_number=ticket.service_number)


class Request(BaseModel):
    client_id: int
    service_number: int
