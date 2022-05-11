from dataclasses import dataclass, field
from pydantic.main import BaseModel

from application.rpc.base_rpc import Rpc, RpcRequest, RpcError

NATS_TOPIC = "bruin.ticket.note.append.request"


@dataclass
class AppendNoteToTicketRpc(Rpc):
    topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, ticket_id: int, note: str) -> bool:
        """
        Appends a single text note to a ticket.

        Communication errors will be raised up as an RpcError.

        Targets:
        - topic: bruin.ticket.note.append.request
        - action: POST /api/Ticket/{ticket_id}/notes

        :param ticket_id: the ticket to which append the note
        :param note: the note to be appended
        :return if the note was appended or not
        """
        request_id, logger = self.start()
        logger.debug(f"__call__(ticket_id={ticket_id}, note=*may contain sensitive information*)")

        try:
            body = RequestBody(ticket_id=ticket_id, note=note)
            request = Request(request_id=request_id, body=body)
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


class Request(RpcRequest):
    body: 'RequestBody'


class RequestBody(BaseModel):
    ticket_id: int
    note: str


# Resolve forward refs for pydantic
Request.update_forward_refs()
