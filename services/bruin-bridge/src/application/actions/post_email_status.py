import json
import logging
from dataclasses import dataclass
from http import HTTPStatus

from application.clients.bruin_client import BruinClient
from application.clients.bruin_session import BruinPostBody, BruinPostRequest
from application.repositories.utils_repository import to_json_bytes
from application.services.sentence_formatter import SentenceFormatter
from nats.aio.msg import Msg
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

BRUIN_PATH = "/api/Email/status"
RESOLUTION_PATTERN = "Marked as {status} by {actor}"


@dataclass
class PostEmailStatus:
    bruin_client: BruinClient
    sentence_formatter: SentenceFormatter

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        try:
            message_body = MessageBody.parse_obj(payload.get("body"))
        except ValidationError as e:
            logger.warning(f"Wrong request message: msg={payload}, validation_error={e}")
            await msg.respond(to_json_bytes({"status": HTTPStatus.BAD_REQUEST, "body": e.errors()}))
            return

        body = PostBody(
            email_id=message_body.email_id,
            status=message_body.email_status,
            resolution=self.sentence_formatter.email_marked_as(message_body.email_status),
            updated_by=self.sentence_formatter.subject(),
        )
        post_request = BruinPostRequest(path=BRUIN_PATH, body=body)

        logger.info(f"Setting email status: post_request={post_request}")
        response = await self.bruin_client._bruin_session.post(post_request)

        if response.status == HTTPStatus.UNAUTHORIZED:
            logger.error(f"Got 401 from Bruin. Re-logging in...")
            await self.bruin_client.login()

        await msg.respond(to_json_bytes({"status": response.status, "body": response.body}))


class MessageBody(BaseModel):
    email_id: int
    email_status: str


class PostBody(BruinPostBody):
    email_id: int = Field(alias="emailId")
    status: str
    resolution: str
    updated_by: str = Field(alias="updatedBy")
