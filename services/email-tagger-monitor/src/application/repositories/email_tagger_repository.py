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
class EmailTaggerRepository:
    _event_bus: Client
    _config: Any
    _notifications_repository: NotificationsRepository

    def __post_init__(self):
        self._timeout = self._config.MONITOR_CONFIG["nats_request_timeout"]["kre_seconds"]

    async def get_prediction(self, email_data: dict):
        email_id = email_data["email"]["email_id"]

        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_prediction():
            err_msg = None

            log.info(f"Sending email data to get prediction: {email_id}")
            request_msg = {"request_id": uuid(), "body": email_data}
            try:
                response = await self._event_bus.request(
                    "email_tagger.prediction.request", to_json_bytes(request_msg), timeout=self._timeout
                )
                response = json.loads(response.data)

            except Exception as ex:
                err_msg = f"An error occurred when sending emails to Email Tagger for email_id '{email_id}' -> {ex}"
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while getting prediction for email "{email_id}" in '
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                log.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                log.info(f"Prediction request sent for email {email_id} to Email Tagger")

            return response

        try:
            return await get_prediction()
        except Exception as e:
            log.error(f"Error trying to get tag prediction from KRE [email_id='{email_id}']: {e}")

    async def save_metrics(self, email_data: dict, ticket_data: dict):
        email_id = email_data["email"]["email_id"]
        ticket_id = ticket_data["ticket_id"]

        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def save_metrics():
            err_msg = None
            log.info(f"Sending email and ticket data to save_metrics: {email_id}")
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "original_email": email_data,
                    "ticket": ticket_data,
                },
            }
            try:
                response = await self._event_bus.request(
                    "email_tagger.metrics.request", to_json_bytes(request_msg), timeout=self._timeout
                )
                response = json.loads(response.data)

            except Exception as ex:
                err_msg = f"An error occurred when sending emails to Email Tagger for email_id '{email_id}' -> {ex}"
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while saving metrics for email "{email_id}" in '
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                log.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                log.info(f"SaveMetrics request sent for email {email_id} and ticket {ticket_id} to Email Tagger")

            return response

        try:
            return await save_metrics()
        except Exception as e:
            log.error(f"Error trying to send metrics to KRE [email_id='{email_id}', ticket_id='{ticket_id}']: {e}")
