import json
import logging
from dataclasses import dataclass
from http import HTTPStatus

from nats.aio.msg import Msg
from pydantic import BaseModel, Field, ValidationError

from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostBody, BruinPostRequest
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)

BRUIN_PATH = "/api/Ticket/{ticket_id}/subscribeUser"


@dataclass
class SubscribeUser:
    bruin_client: BruinClient

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        try:
            message_body = MessageBody.parse_obj(payload.get("body"))
        except ValidationError as e:
            logger.warning(f"Wrong request message: msg={payload}, validation_error={e}")
            await msg.respond(to_json_bytes({"status": HTTPStatus.BAD_REQUEST, "body": e.errors()}))
            return

        path = BRUIN_PATH.format(ticket_id=message_body.ticket_id)
        body = PostBody(
            subscription_type=message_body.subscription_type, user=PostBodyUser(email=message_body.user_email)
        )
        post_request = BruinPostRequest(path=path, body=body)

        logger.info(f"Subscribing user: post_request={post_request}")
        response = await self.bruin_client._bruin_session.post(post_request)

        if response.status == HTTPStatus.UNAUTHORIZED:
            logger.error(f"Got 401 from Bruin. Re-logging in...")
            await self.bruin_client.login()

        await msg.respond(to_json_bytes({"status": response.status, "body": response.body}))


class MessageBody(BaseModel):
    ticket_id: int
    user_email: str
    subscription_type: str


class PostBodyUser(BaseModel):
    email: str = Field(repr=False)


class PostBody(BruinPostBody):
    subscription_type: str = Field(alias="subscriptionType")
    user: PostBodyUser
