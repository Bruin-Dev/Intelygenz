import json
import logging
from dataclasses import dataclass
from typing import Any

from framework.nats.client import Client
from shortuuid import uuid
from tenacity import retry, stop_after_delay, wait_exponential

from application.repositories import nats_error_response
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils import to_json_bytes

log = logging.getLogger(__name__)


@dataclass
class BruinRepository:
    _event_bus: Client
    _config: Any
    _notifications_repository: NotificationsRepository

    def __post_init__(self):
        self._timeout = self._config.MONITOR_CONFIG["nats_request_timeout"]["post_email_tag_seconds"]

    async def post_email_tag(self, email_id, tag_id):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def post_email_tag():
            err_msg = None
            log.info(f'Sending tag "{tag_id}" for email_id: {email_id}')
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "email_id": email_id,
                    "tag_id": tag_id,
                },
            }
            try:
                response = await self._event_bus.request(
                    "bruin.email.tag.request", to_json_bytes(request_msg), timeout=self._timeout
                )
                response = json.loads(response.data)

            except Exception as ex:
                err_msg = (
                    f"An error occurred when sending tags to Bruin API, "
                    f'with tags {tag_id} for email_id "{email_id}" -> {ex}'
                )
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status == 409:
                    log.info(f"Got 409 from Bruin. Tag already present for email_id {email_id} and tag_id {tag_id}")
                elif response_status not in range(200, 300):
                    err_msg = (
                        f"Error sending tags {tag_id} belonging to email {email_id} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                log.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                log.info(f"Tags for email {email_id} sent to Bruin")

            return response

        try:
            return await post_email_tag()
        except Exception as e:
            log.error(f"Error sending tags {tag_id} to Bruin [email_id='{email_id}']: {e}")

    async def get_single_ticket_basic_info(self, ticket_id):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_single_ticket_basic_info():
            err_msg = None
            log.info(f'Getting ticket "{ticket_id}" basic info')
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "ticket_id": ticket_id,
                },
            }
            try:
                response = await self._event_bus.request(
                    "bruin.single_ticket.basic.request", to_json_bytes(request_msg), timeout=self._timeout
                )
                response = json.loads(response.data)
            except Exception as err:
                err_msg = f"An error occurred when getting basic info from Bruin, for ticket_id '{ticket_id}' -> {err}"
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f"Error getting basic info for ticket {ticket_id} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
                else:
                    response["body"] = {
                        "ticket_id": ticket_id,
                        "ticket_status": response["body"]["ticketStatus"],
                        "call_type": response["body"]["callType"],
                        "category": response["body"]["category"],
                        "creation_date": response["body"]["createDate"],
                    }

            if err_msg:
                log.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                log.info(f"Basic info for ticket {ticket_id} retrieved from Bruin")

            return response

        try:
            return await get_single_ticket_basic_info()
        except Exception as e:
            log.error(f"Error getting ticket {ticket_id} from Bruin: {e}")
