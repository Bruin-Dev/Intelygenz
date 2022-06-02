from dataclasses import dataclass, field
from pydantic import BaseModel

from application.rpc import Rpc, RpcError

NATS_TOPIC = "bruin.ticket.note.append.request"


@dataclass
class AppendNoteToTicketRpc(Rpc):
    topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, ticket_id: int, note: str) -> bool:
        """
        Appends a single Note to a Ticket.

        Communication errors will be raised up as an RpcError.

        Targets:
        - topic: bruin.ticket.note.append.request
        - action: POST /api/Ticket/{ticket_id}/notes

        :param ticket_id: the Ticket to which append the note
        :param note: the Note to be appended
        :return if the Note was appended or not
        """
        request, logger = self.start()
        logger.debug(f"__call__(ticket_id={ticket_id}, note=*may contain sensitive information*)")

        try:
            request.body = RequestBody(ticket_id=ticket_id, note=note)
            response = await self.send(request)

            if response.is_ok():
                logger.debug(f"__call__(): [OK] response=("
                             f"status={response.status}, "
                             f"body=*may contain sensitive information*)")
                return True
            else:
                logger.warning(f"__call__(): [KO] response=({response})")
                return False

        except Exception as e:
            raise RpcError from e


class RequestBody(BaseModel):
    ticket_id: int
    note: str


RequestBody.update_forward_refs()
