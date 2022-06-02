from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from application.rpc import Rpc

NATS_TOPIC = "bruin.ticket.note.append.request"


@dataclass
class AppendNoteToTicketRpc(Rpc):
    topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, ticket_id: str, note: str) -> bool:
        """
        Appends a single Note to a Ticket.
        Proxied service: POST /api/Ticket/{ticket_id}/notes
        :param ticket_id: the Ticket to which append the note
        :param note: the Note to be appended
        :return if the Note was appended or not
        """
        request, logger = self.start()
        logger.debug(f"__call__(ticket_id={ticket_id}, note=**)")

        request.body = RequestBody(ticket_id=ticket_id, note=note)
        await self.send(request)

        logger.debug(f"__call__() [OK]")
        return True


class RequestBody(BaseModel):
    ticket_id: str
    note: str = Field(repr=False)
