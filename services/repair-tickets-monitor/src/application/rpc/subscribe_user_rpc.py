from http import HTTPStatus

from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from application.rpc import Rpc, RpcFailedError

NATS_TOPIC = "bruin.subscribe.user"


@dataclass
class SubscribeUserRpc(Rpc):
    topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, ticket_id: int, user_email: str) -> bool:
        """
        Subscribes a user to a Ticket notifications.
        The user will be created if it doesn't yet exist.
        FORBIDDEN and INTERNAL_SERVER_ERROR responses are considered as
        the user couldn't be subscribed to the Ticket and won't raise any
        an Exception.
        Proxied service: POST /api/Ticket/{ticket_id}/subscribeUser
        :raise RpcFailedError: whenever any other response other than OK, FORBIDDEN or INTERNAL_SERVER_ERROR was received
        :param ticket_id: the Ticket to which subscribe the User
        :param user_email: the User being subscribed email
        :return if the User was subscribed or not
        """
        request, logger = self.start()
        logger.debug(f"__call__(ticket_id={ticket_id}, user_email=**)")
        request.body = RequestBody(ticket_id=ticket_id, user_email=user_email)

        try:
            await self.send(request)
           
            logger.debug(f"__call__() [OK]")
            return True

        except RpcFailedError as error:
            if error.response.status in [HTTPStatus.FORBIDDEN, HTTPStatus.INTERNAL_SERVER_ERROR]:
                return False
            else:
                raise error


class RequestBody(BaseModel):
    ticket_id: int
    user_email: str = Field(repr=False)
