from http import HTTPStatus
from logging import Logger
from typing import Any

from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostBody, BruinPostRequest, BruinResponse
from application.services.sentence_formatter import SentenceFormatter
from dataclasses import dataclass
from igz.packages.eventbus.eventbus import EventBus
from pydantic import BaseModel, Field, ValidationError

BRUIN_PATH = "/api/Email/status"
RESOLUTION_PATTERN = "Marked as {status} by {actor}"


@dataclass
class PostEmailStatus:
    logger: Logger
    event_bus: EventBus
    bruin_client: BruinClient
    sentence_formatter: SentenceFormatter

    async def post_email_status(self, msg: Any):
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

        body = PostBody(
            email_id=message_body.email_id,
            status=message_body.email_status,
            resolution=self.sentence_formatter.email_marked_as(message_body.email_status),
            updated_by=self.sentence_formatter.subject(),
        )
        post_request = BruinPostRequest(path=BRUIN_PATH, body=body)

        self.logger.info(f"Setting email status: post_request={post_request}")
        # response = await self.bruin_client._bruin_session.post(post_request)
        response = BruinResponse(status=200, body="")

        if response.status == HTTPStatus.UNAUTHORIZED:
            self.logger.error(f"Got 401 from Bruin. Re-logging in...")
            await self.bruin_client.login()

        await self.event_bus.publish_message(
            response_topic, {"request_id": request_id, "status": response.status, "body": response.body}
        )


class MessageBody(BaseModel):
    email_id: int
    email_status: str


class PostBody(BruinPostBody):
    email_id: int = Field(alias="emailId")
    status: str
    resolution: str
    updated_by: str = Field(alias="updatedBy")
