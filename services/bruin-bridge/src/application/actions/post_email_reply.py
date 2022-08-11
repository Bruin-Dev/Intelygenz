from http import HTTPStatus
from logging import Logger
from typing import Any

from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostRequest
from dataclasses import dataclass
from igz.packages.eventbus.eventbus import EventBus
from pydantic import BaseModel, ValidationError

# TODO: to be changed to the actual path
BRUIN_PATH = "/api/Notification/email/ReplyAll"


@dataclass
class PostEmailReply:
    logger: Logger
    event_bus: EventBus
    bruin_client: BruinClient

    async def post_email_reply(self, msg: Any):
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

        self.logger.info(f"Sending email {message_body.parent_email_id} an auto-reply")
        path = BRUIN_PATH.format(email_id=message_body.parent_email_id)
        post_body = PostBody(content=message_body.reply_body, email_id=message_body.parent_email_id)
        post_params = PostParams(isContentHTMLEncoded=message_body.html_reply_body)
        post_request = BruinPostRequest(path=path, params=post_params.dict(), body=post_body)
        response = await self.bruin_client._bruin_session.post(post_request)

        if response.status == HTTPStatus.UNAUTHORIZED:
            self.logger.error(f"Got 401 from Bruin. Re-logging in...")
            await self.bruin_client.login()

        await self.event_bus.publish_message(
            response_topic, {"request_id": request_id, "status": response.status, "body": response.body}
        )


class MessageBody(BaseModel):
    parent_email_id: int
    reply_body: str
    html_reply_body: bool = True


class PostBody(BaseModel):
    content: str
    email_id: int


class PostParams(BaseModel):
    isContentHTMLEncoded: bool