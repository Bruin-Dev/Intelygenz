import json
import logging

from nats.aio.msg import Msg

from ..repositories.slack_repository import SlackRepository

logger = logging.getLogger(__name__)


class SendToSlack:
    def __init__(self, slack_repository: SlackRepository):
        self._slack_repository = slack_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if "message" not in payload.keys():
            logger.error(f'Cannot send to slack with {json.dumps(payload)}. Need parameters "message"')

            response["status"] = 400
            response["body"] = 'Must include "message" in request body'
            await msg.respond(json.dumps(response).encode())
            return

        message = payload["message"]
        logger.info(f"Sending msg {message} to slack...")
        slack_response = await self._slack_repository.send_to_slack(message)
        response["body"] = slack_response.body
        response["status"] = slack_response.status

        await msg.respond(json.dumps(response).encode())
        logger.info(
            f"Notifications send to slack published in event bus for request {json.dumps(payload)}."
            f" Message published was {response}"
        )
