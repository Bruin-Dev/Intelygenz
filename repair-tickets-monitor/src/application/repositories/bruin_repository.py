from typing import List
from shortuuid import uuid

from tenacity import retry, wait_exponential, stop_after_delay

from application.repositories import nats_error_response


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._timeout = self._config.MONITOR_CONFIG["nats_request_timeout"][
            "post_ticket_seconds"
        ]

    async def get_site(self, client_id, site_id):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_site():
            err_msg = None
            self._logger.info(
                f"Getting site for client_id={client_id} and site_id={site_id}"
            )
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "client_id": client_id,
                    "site_id": site_id,
                },
            }
            try:
                response = await self._event_bus.rpc_request(
                    "bruin.get.site", request_msg, timeout=self._timeout
                )
            except Exception as err:
                err_msg = (
                    f"An error occurred when getting site from Bruin, "
                    f'for client_id "{client_id}" and site_id "{site_id}" -> {err}'
                )
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f"Error getting basic info for client_id={client_id} and site_id={site_id} in "
                        f"{self._config.ENVIRONMENT.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
                else:
                    # TODO: review - return as array or just the first element or none if empty
                    response["body"] = {"site": response["body"].get("documents", [])}

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f'Site for client_id "{client_id}" and site_id "{site_id}" retrieved from Bruin'
                )

            return response

        try:
            return await get_site()
        except Exception as e:
            self._logger.error(
                f"Error getting client_id={client_id} and site_id={site_id} from Bruin: {e}"
            )

    async def get_client_info(self, client_id, service_number):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"],
                min=self._config.NATS_CONFIG["min"],
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_client_info():
            err_msg = None
            self._logger.info(
                f"Getting client_info for client_id={client_id} and service_number={service_number}"
            )
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "client_id": client_id,
                    "service_number": service_number,
                },
            }
            try:
                response = await self._event_bus.rpc_request(
                    "bruin.customer.get.info", request_msg, timeout=self._timeout
                )
            except Exception as err:
                err_msg = (
                    f"An error occurred when getting client_info from Bruin, "
                    f'for client_id "{client_id}" and service_number "{service_number}" -> {err}'
                )
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error getting basic info for client_id "{client_id}" and \
                          service_number "{service_number}" in '
                        f"{self._config.ENVIRONMENT.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )
                else:
                    # TODO: review - return as array or just the first element or none if empty
                    response["body"] = {"site": response["body"].get("documents", [])}

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f'client_info for client_id "{client_id}" and service_number "{service_number}" '
                    f"retrieved from Bruin"
                )

            return response

        try:
            return await get_client_info()
        except Exception as e:
            self._logger.error(
                f'Error getting client_id "{client_id}" and service_number "{service_number}" '
                f"from Bruin: {e}"
            )

    async def create_outage_ticket(
        self, client_id: int, service_numbers: List[str], contact_info: dict
    ):
        # endpoint: bruin.ticket.creation.outage.request -- POST /api/Ticket/repair
        err_msg = None

        # TODO: check payload on bruin client
        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "service_numbers": service_numbers,
                "local_contact": contact_info,
            },
        }

        try:
            self._logger.info(
                f"Creating outage ticket for {service_numbers} that belongs to client {client_id}..."
            )
            response = await self._event_bus.rpc_request(
                "bruin.ticket.creation.outage.request", request, timeout=30
            )
            self._logger.info(
                f"Outage ticket for {service_numbers} that belongs to client {client_id} created!"
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when creating outage ticket for device {service_numbers} belong to client"
                f"{client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            is_bruin_custom_status = response_status in (409, 471, 472, 473)
            if not (response_status in range(200, 300) or is_bruin_custom_status):
                err_msg = (
                    f"Error while creating outage ticket for {service_numbers} that belongs to client "
                    f"{client_id} in {self._config.ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_affecting_ticket(
        self, client_id: int, service_numbers: List[str], contact_info: dict
    ):
        # endpoint: bruin.ticket.creation.request -- POST /api/Ticket
        err_msg = None

        # TODO: check payload on bruin client
        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "service_numbers": service_numbers,
                "contact": contact_info,
            },
        }

        try:
            self._logger.info(
                f"Creating affecting ticket for {service_numbers} that belongs to client {client_id}..."
            )
            response = await self._event_bus.rpc_request(
                "bruin.ticket.creation.request", request, timeout=30
            )
            self._logger.info(
                f"Outage ticket for {service_numbers} that belongs to client {client_id} created!"
            )
        except Exception as e:
            err_msg = (
                f"An error occurred when creating affecting ticket for device {service_numbers} belong to client"
                f"{client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            is_bruin_custom_status = response_status in (409, 471, 472, 473)
            if not (response_status in range(200, 300) or is_bruin_custom_status):
                err_msg = (
                    f"Error while creating affecting ticket for {service_numbers} that belongs to client "
                    f"{client_id} in {self._config.ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
