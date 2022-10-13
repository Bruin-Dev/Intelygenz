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

# TODO: to be changed to the actual path
BRUIN_PATH = "/api/Notification/email/ReplyAll"


@dataclass
class PostEmailReply:
    bruin_client: BruinClient

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        try:
            message_body = MessageBody.parse_obj(payload.get("body"))
        except ValidationError as e:
            logger.warning(f"Wrong request message: msg={payload}, validation_error={e}")
            await msg.respond(to_json_bytes({"status": HTTPStatus.BAD_REQUEST, "body": e.errors()}))
            return

        logger.info(f"Sending email {message_body.parent_email_id} an auto-reply")
        path = BRUIN_PATH.format(email_id=message_body.parent_email_id)
        post_body = PostBody(content=message_body.reply_body, email_id=message_body.parent_email_id)
        post_params = PostParams(isContentHTMLEncoded=message_body.html_reply_body)
        post_request = BruinPostRequest(path=path, params=post_params.dict(), body=post_body)
        response = await self.bruin_client._bruin_session.post(post_request)

        if response.status == HTTPStatus.UNAUTHORIZED:
            logger.error(f"Got 401 from Bruin. Re-logging in...")
            await self.bruin_client.login()

        await msg.respond(to_json_bytes({"status": response.status, "body": response.body}))


class MessageBody(BaseModel):
    parent_email_id: int
    reply_body: str
    html_reply_body: bool = True


class PostBody(BruinPostBody):
    content: str
    email_id: int = Field(alias="emailId")


class PostParams(BaseModel):
    isContentHTMLEncoded: bool
