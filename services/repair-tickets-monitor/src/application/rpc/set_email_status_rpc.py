import logging

from application.domain.email import EmailStatus
from application.rpc import Rpc, RpcRequest
from dataclasses import dataclass, field
from pydantic import BaseModel

log = logging.getLogger(__name__)

NATS_TOPIC = "bruin.email.status"


@dataclass
class SetEmailStatusRpc(Rpc):
    _topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, email_id: str, email_status: EmailStatus):
        """
        Sets the status of an email.
        :raise RpcFailedError: whenever any other response other than OK was received
        :param email_id: the email id which status should be changed
        :param email_status: the new status the email must be set to
        :return if the User was subscribed or not
        """
        log.debug(f"__call__(email_id={email_id}, email_status={email_status})")

        request = RpcRequest(body=RequestBody(email_id=email_id, email_status=_map_email_status(email_status)))
        await self.send(request)

        log.debug(f"__call__() [OK]")


class RequestBody(BaseModel):
    email_id: str
    email_status: str


def _map_email_status(email_status: EmailStatus) -> str:
    if email_status == EmailStatus.AIQ:
        return "AIQ"
    elif email_status == EmailStatus.NEW:
        return "New"
    else:
        return "Done"
