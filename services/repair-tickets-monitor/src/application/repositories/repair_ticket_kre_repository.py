from shortuuid import uuid

from tenacity import retry, wait_exponential, stop_after_delay

from application.repositories import nats_error_response
from typing import Any, Dict, List


class RepairTicketKreRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._timeout = self._config.MONITOR_CONFIG['nats_request_timeout']['kre_seconds']

    async def get_email_inference(self, email_data: Dict[str, Any], tag_info: Dict[str, Any]):
        email_id = email_data["email"]["email_id"]
        tag_name = self._config.MONITOR_CONFIG['tag_ids'].get(tag_info['tag_id'])
        payload = {
            "email_id": email_data["email"]["email_id"],
            "client_id": email_data["email"]["client_id"],
            "subject": email_data["email"]["client_id"],
            "body": email_data["email"]["body"],
            "from_address": email_data["email"]["from"],
            "to": email_data["email"]["to"],
            "cc": email_data["email"]["cc"],
            "date": email_data["email"]["date"],
            "tag": {
                "type": tag_name,
                "probability": tag_info['probability'],
            }
        }

        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_email_inference():
            err_msg = None

            self._logger.info(
                f"Sending email data to get prediction for email_id={email_id}"
            )
            request_msg = {"request_id": uuid(), "body": payload}
            try:
                response = await self._event_bus.rpc_request(
                    "rta.prediction.request", request_msg, timeout=self._timeout
                )

            except Exception as e:
                err_msg = f"An error occurred when sending emails to rta for email_id '{email_id}' -> {e}"
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while getting prediction for email "{email_id}" in '
                        f"{self._config.ENVIRONMENT.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f"Prediction request sent for email {email_id} to rta"
                )

            return response

        try:
            return await get_email_inference()
        except Exception as e:
            self._logger.error(
                f"Error trying to get prediction from rta KRE [email_id='{email_id}']: {e}"
            )

    async def save_outputs(
            self,
            email_id: str,
            service_numbers_site_map: Dict[str, str],
            tickets_created: List[Dict[str, Any]],
            ticket_updated: List[Dict[str, Any]],
            tickets_could_be_created: List[Dict[str, Any]],
            tickets_could_be_updated: List[Dict[str, Any]],
            tickets_cannot_be_created: List[Dict[str, Any]],
    ):
        validated_service_numbers = list(service_numbers_site_map.keys())

        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def save_outputs():
            err_msg = None

            self._logger.info(
                f"Sending output data for email_id={email_id}"
            )

            request_body = {
                'email_id': email_id,
                'validated_service_numbers': validated_service_numbers,
                'service_numbers_site_map': service_numbers_site_map,
                'tickets_created': tickets_created,
                'tickets_updated': ticket_updated,
                'tickets_could_be_created': tickets_could_be_created,
                'tickets_could_be_updated': tickets_could_be_updated,
                'tickets_cannot_be_created': tickets_cannot_be_created,
            }
            request_msg = {
                "request_id": uuid(),
                "body": request_body
            }
            try:
                response = await self._event_bus.rpc_request(
                    "rta.save_outputs.request", request_msg, timeout=self._timeout
                )

            except Exception as e:
                err_msg = f"An error occurred when saving output to rta for email_id '{email_id}' -> {e}"
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while saving outputs for email "{email_id}" in '
                        f"{self._config.ENVIRONMENT.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f"Saving Output request sent for email {email_id} to rta"
                )

            return response

        try:
            return await save_outputs()
        except Exception as e:
            self._logger.error(
                f"Error trying to get save output from rta KRE [email_id='{email_id}']: {e}"
            )

    async def save_created_ticket_feedback(self, email_data: dict, ticket_data: dict):
        email_id = email_data['email']['email_id']
        ticket_id = ticket_data['ticket_id']

        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def save_created_ticket_feedback():
            err_msg = None
            self._logger.info(f"Sending email and ticket data to save_created_tickets: {email_id}")
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "original_email": email_data,
                    "ticket": ticket_data,
                }
            }
            try:
                response = await self._event_bus.rpc_request("repair_ticket_automation.save_created_tickets.request",
                                                             request_msg,
                                                             timeout=self._timeout)

            except Exception as e:
                err_msg = f'An error occurred when sending emails to RTA for ticket_id "{ticket_id}"' \
                          f' and email_id  "{email_id}" -> {e}'
                response = nats_error_response
            else:
                response_body = response['body']
                response_status = response['status']

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while saving created ticket feedback for email with ticket_id "{ticket_id}"'
                        f'and email_id "{email_id}" in {self._config.ENVIRONMENT.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f'SaveCreatedTicketFeedback request sent for email {email_id} and ticket {ticket_id} to RTA')

            return response

        try:
            return await save_created_ticket_feedback()
        except Exception as e:
            self._logger.error(
                f"Error trying to save_created tickets feedback to KRE "
                f"[email_id='{email_id}', ticket_id='{ticket_id}']: {e}"
            )
