import logging
from dataclasses import dataclass

from shared import NatsClient

from .ticket import Ticket

log = logging.getLogger(__name__)


@dataclass
class StoreTicketSettings:
    pass


@dataclass
class StoreTicket:
    settings: StoreTicketSettings
    nats_client: NatsClient

    async def __call__(self, ticket: Ticket):
        log.debug(f"store(ticket={ticket})")
        # TODO
