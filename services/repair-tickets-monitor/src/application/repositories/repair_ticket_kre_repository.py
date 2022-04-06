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
        self._timeout = self._config.MONITOR_CONFIG["nats_request_timeout"]["kre_seconds"]

    async def get_email_inference(self, email_data: Dict[str, Any], tag_info: Dict[str, Any]):
        email_id = email_data["email_id"]
        payload = {
            **email_data,
            "tag": {
                "type": "Repair",
                "probability": tag_info["tag_probability"],
            },
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

            self._logger.info("email_id=%s Sending email data to get prediction", email_id)
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

                if response_status not in range(200, 400):
                    err_msg = (
                        f'Error while getting prediction for email "{email_id}" in '
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

                elif response_status == 400:
                    err_msg = (
                        f'Cannot get prediction for "{email_id}" in '
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"reason {response_body}"
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info("email_id=%s Prediction request sent to rta", email_id)

            return response

        try:
            return await get_email_inference()
        except Exception as e:
            self._logger.error("email_id=%s Error trying to get prediction from rta KRE %e", email_id, e)

    async def save_outputs(
        self,
        email_id: str,
        service_numbers_sites_map: Dict[str, str],
        tickets_created: List[Dict[str, Any]],
        tickets_updated: List[Dict[str, Any]],
        tickets_could_be_created: List[Dict[str, Any]],
        tickets_could_be_updated: List[Dict[str, Any]],
        tickets_cannot_be_created: List[Dict[str, Any]],
        validated_ticket_numbers: List[Dict[str, Any]],
        bruin_ticket_status_map: List[Dict[str, Any]],
        bruin_ticket_call_type_map: List[Dict[str, Any]],
        bruin_ticket_category_map: List[Dict[str, Any]]
    ):
        validated_service_numbers = list(service_numbers_sites_map.keys())

        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def save_outputs():
            request_id = uuid()
            request_msg = {
                "request_id": request_id,
                "body": {
                    "email_id": email_id,
                    "validated_service_numbers": validated_service_numbers,
                    "service_numbers_sites_map": service_numbers_sites_map,
                    "tickets_created": tickets_created,
                    "tickets_updated": tickets_updated,
                    "tickets_could_be_created": tickets_could_be_created,
                    "tickets_could_be_updated": tickets_could_be_updated,
                    "tickets_cannot_be_created": tickets_cannot_be_created,
                    "validated_ticket_numbers": validated_ticket_numbers,
                    "bruin_ticket_status_map": bruin_ticket_status_map,
                    "bruin_ticket_call_type_map": bruin_ticket_call_type_map,
                    "bruin_ticket_category_map": bruin_ticket_category_map
                },
            }
            self._logger.info(
                "request_id=%s email_id=%s Sending data to save output in repair-tickets-kre-bridge",
                request_id,
                email_id,
            )

            try:
                response = await self._event_bus.rpc_request(
                    "rta.save_outputs.request", request_msg, timeout=self._timeout
                )

            except Exception as exception:
                err_msg = (
                    "request_id=%s email_id=%s "
                    "Exception occurred when getting inference from repair-tickets-kre-bridge: %s"
                    % (request_id, email_id, exception)
                )
                response = nats_error_response
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
                return response

            response_body = response["body"]
            response_status = response["status"]

            if response_status != 200:
                err_msg = (
                    "request_id=%s email_id=%s "
                    "Bad response code received from repair-tickets-kre-bridge: %s - %s"
                    % (
                        request_id,
                        email_id,
                        response_status,
                        response_body,
                    )
                )
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
                return response

            self._logger.info("request_id=%s email_id=%s Output saved", request_id, email_id)
            return response

        return await save_outputs()

    async def save_created_ticket_feedback(self, email_data: dict, ticket_data: dict, site_map: dict):
        email_id = email_data["email_id"]
        ticket_id = ticket_data["ticket_id"]

        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def save_created_ticket_feedback():
            err_msg = None
            self._logger.info(f"Sending email and ticket data to save_created_tickets: {email_id}")
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "ticket_id": str(ticket_data["ticket_id"]),
                    "email_id": email_data["email_id"],
                    "parent_id": email_data["parent_id"],
                    "client_id": email_data["client_id"],
                    "real_service_numbers": ticket_data["service_numbers"],
                    "real_class": ticket_data["category"],
                    "site_map": site_map,
                },
            }
            try:
                response = await self._event_bus.rpc_request(
                    "rta.created_ticket_feedback.request", request_msg, timeout=self._timeout
                )

            except Exception as e:
                err_msg = (
                    f'An error occurred when sending emails to RTA for ticket_id "{ticket_id}"'
                    f' and email_id  "{email_id}" -> {e}'
                )
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while saving created ticket feedback for email with ticket_id "{ticket_id}"'
                        f'and email_id "{email_id}" in {self._config.ENVIRONMENT_NAME.upper()} environment: '
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f"SaveCreatedTicketFeedback request sent for email {email_id} and ticket {ticket_id} to RTA"
                )

            return response

        try:
            return await save_created_ticket_feedback()
        except Exception as e:
            self._logger.error(
                f"Error trying to save_created tickets feedback to KRE "
                f"[email_id='{email_id}', ticket_id='{ticket_id}']: {e}"
            )

    async def save_closed_ticket_feedback(
        self, ticket_id: str, client_id: str, status: str, cancelled_reasons: List[str]
    ):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def save_closed_ticket_feedback():
            err_msg = None
            self._logger.info("ticket_id=%s Sending ticket data to save_closed_tickets", ticket_id)
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "ticket_id": str(ticket_id),
                    "client_id": str(client_id),
                    "ticket_status": status,
                    "cancelled_reasons": cancelled_reasons,
                },
            }
            try:
                response = await self._event_bus.rpc_request(
                    "rta.closed_ticket_feedback.request", request_msg, timeout=self._timeout
                )

            except Exception as e:
                err_msg = f'An error occurred when sending tickets to RTA for ticket_id "{ticket_id} {e}"'
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while saving closed ticket feedback for with ticket_id "{ticket_id}"'
                        f"in {self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info("ticket_id=%s Save closed request sent to RTA", ticket_id)

            return response

        try:
            return await save_closed_ticket_feedback()
        except Exception as e:
            self._logger.error(
                f"Error trying to save closed tickets feedback to KRE " f"[ticket_id='{ticket_id}']: {e}"
            )
