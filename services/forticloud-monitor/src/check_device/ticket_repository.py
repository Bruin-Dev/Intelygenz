import logging
from dataclasses import dataclass

from .ticket import Ticket

log = logging.getLogger(__name__)


@dataclass
class TicketRepository:
    async def store(self, ticket: Ticket):
        log.debug(f"store(ticket={ticket})")
        pass
