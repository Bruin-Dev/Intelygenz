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

    async def get_email_inference(self, email_data: dict):
        email_id = email_data["email"]["email_id"]

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
            request_msg = {"request_id": uuid(), "body": email_data}
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
            service_numbers_by_site: Dict[str, List],
            exiting_ticket_ids: List[str],
            created_ticket_ids: List[str],
    ):
        site_ids = list(service_numbers_by_site.keys())
        service_numbers = [service_number for _, service_number_list in service_numbers_by_site
                           for service_number in service_number_list]

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
                'site_ids': site_ids,
                'validated_service_numbers': service_numbers,
                'existing_tickets_ids': exiting_ticket_ids,
                'created_tickets_ids': created_ticket_ids,
            }
            request_msg = {
                "request_id": uuid(),
                "body": request_body}
            try:
                response = await self._event_bus.rpc_request(
                    "rta.prediction.request", request_msg, timeout=self._timeout
                )

            except Exception as e:
                err_msg = f"An error occurred when saving output to rta for email_id '{email_id}' -> {e}"
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
