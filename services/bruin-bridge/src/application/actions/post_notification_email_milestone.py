import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class PostNotificationEmailMilestone:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        payload = payload.get("body")

        if payload is None:
            response["status"] = 400
            response["body"] = 'Must include {.."body":{"ticket_id", "notification_type", "service_number"}, in request'
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in payload.keys() for key in ("ticket_id", "notification_type", "service_number")):
            logger.error(f"Cannot send milestone email using {json.dumps(payload)}. JSON malformed")

            response["body"] = (
                'You must include "ticket_id", "notification_type" and "service_number"'
                ' in the "body" field of the response request'
            )
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        ticket_id = payload.get("ticket_id")
        notification_type = payload.get("notification_type")
        service_number = payload.get("service_number")

        logger.info(
            f'Sending milestone email for ticket "{ticket_id}", service number "{service_number}"'
            f' and notification type "{notification_type}"...'
        )

        result = await self._bruin_repository.post_notification_email_milestone(payload)

        response["body"] = result["body"]
        response["status"] = result["status"]
        if response["status"] in range(200, 300):
            logger.info(
                f"Milestone email notification successfully sent for ticket {ticket_id}, service number"
                f" {service_number} and notification type {notification_type}"
            )
        else:
            logger.error(
                f"Error sending milestone email notification for ticket {ticket_id}, service number"
                f" {service_number} and notification type {notification_type}: Status:"
                f' {response["status"]} body: {response["body"]}'
            )

        await msg.respond(to_json_bytes(response))
