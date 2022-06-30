from typing import Dict

from application.actions.monitoring import GatewayPair
from application.dataclasses import Gateway
from shortuuid import uuid


class ServiceNowRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def check_active_incident_tickets_for_gateway(self, unhealthy_gateway: Gateway):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "host": unhealthy_gateway.host,
                "gatewayId": unhealthy_gateway.id,
            },
        }

        try:
            self._logger.info(
                f"Getting active incident tickets info from ServiceNow for host {unhealthy_gateway.host}..."
            )
            response = await self._event_bus.rpc_request("", request, timeout=30)
        except Exception as e:
            err_msg = f"An error occurred when requesting active incident tickets from ServiceNow -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Got active incident tickets info from ServiceNow for host {unhealthy_gateway.host}!"
                )
            else:
                environment = self._config.ENVIRONMENT_NAME.upper()
                err_msg = (
                    f"Error while retrieving active incidents tickets from ServiceNow in {environment} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
