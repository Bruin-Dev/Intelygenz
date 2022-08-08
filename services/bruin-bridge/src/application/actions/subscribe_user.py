from http import HTTPStatus
from logging import Logger
from typing import Any

from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostBody, BruinPostRequest, BruinResponse
from dataclasses import dataclass
from igz.packages.eventbus.eventbus import EventBus
from pydantic import BaseModel, Field, ValidationError

BRUIN_PATH = "/api/Ticket/{ticket_id}/subscribeUser"


@dataclass
class SubscribeUser:
    logger: Logger
    event_bus: EventBus
    bruin_client: BruinClient

    async def subscribe_user(self, msg: Any):
        request_id = msg.get("request_id")
        response_topic = msg.get("response_topic")

        try:
            message_body = MessageBody.parse_obj(msg.get("body"))
        except ValidationError as e:
            self.logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
            await self.event_bus.publish_message(
                response_topic, {"request_id": request_id, "status": HTTPStatus.BAD_REQUEST, "body": e.errors()}
            )
            return

        path = BRUIN_PATH.format(ticket_id=message_body.ticket_id)
        body = PostBody(
            subscription_type=message_body.subscription_type, user=PostBodyUser(email=message_body.user_email)
        )
        post_request = BruinPostRequest(path=path, body=body)

        self.logger.info(f"Subscribing user: post_request={post_request}")
        # response = await self.bruin_client._bruin_session.post(post_request)
        response = BruinResponse(status=200, body="1234")

        if response.status == HTTPStatus.UNAUTHORIZED:
            self.logger.error(f"Got 401 from Bruin. Re-logging in...")
            await self.bruin_client.login()

        await self.event_bus.publish_message(
            response_topic, {"request_id": request_id, "status": response.status, "body": response.body}
        )


class MessageBody(BaseModel):
    ticket_id: int
    user_email: str
    subscription_type: str


class PostBodyUser(BaseModel):
    email: str = Field(repr=False)


class PostBody(BruinPostBody):
    subscription_type: str = Field(alias="subscriptionType")
    user: PostBodyUser
