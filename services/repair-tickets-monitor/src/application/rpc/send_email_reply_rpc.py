import logging
from dataclasses import dataclass, field

from pydantic import BaseModel

from application.rpc import Rpc, RpcFailedError, RpcRequest

log = logging.getLogger(__name__)

NATS_TOPIC = "bruin.email.reply"


@dataclass
class SendEmailReplyRpc(Rpc):
    _topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, parent_email_id: str, reply_body: str) -> str:
        """
        Replies to the parent_email_id with a given body.
        The email address to which the reply will be automatically selected on the server.
        :param parent_email_id: parent email to which reply
        :param reply_body: the body that will be sent
        :return: the ID of the sent reply
        """
        log.debug(f"__call__(parent_email_id={parent_email_id}, reply_body={reply_body}")

        request = RpcRequest(body=RequestBody(parent_email_id=parent_email_id, reply_body=reply_body))
        response = await self.send(request)

        log.debug(f"__call__(): response={response}")
        try:
            return str(int(response.body))
        except (ValueError, TypeError) as error:
            raise RpcFailedError(request=request, response=response) from error


class RequestBody(BaseModel):
    parent_email_id: str
    reply_body: str
