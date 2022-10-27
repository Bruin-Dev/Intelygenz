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

        if payload.get("body") is None:
            logger.error(f"Cannot send to slack with {json.dumps(payload)}. JSON malformed")
            return

        if not all(key in payload["body"].keys() for key in ("message",)):
            logger.error(f'Cannot send to slack with {json.dumps(payload)}. Need parameters "message"')
            return

        message = payload["body"]["message"]
        logger.info(f"Sending msg {message} to slack...")
        await self._slack_repository.send_to_slack(message)
        logger.info(f"Notifications send to slack for request {json.dumps(payload)}.")
