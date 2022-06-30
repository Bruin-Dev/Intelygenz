from datetime import datetime, timedelta

from shortuuid import uuid


class VelocloudRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_network_gateway_status_list(self, velocloud_host: str, lookup_interval: int) -> dict:
        err_msg = None
        metrics = ["tunnelCount"]
        since = datetime.now() - timedelta(seconds=lookup_interval)

        request = {
            "request_id": uuid(),
            "body": {
                "host": velocloud_host,
                "metrics": metrics,
                "since": since.isoformat() + "Z",
            },
        }

        try:
            self._logger.info(
                f"Getting network gateway status list from Velocloud host {velocloud_host} "
                f"for the past {lookup_interval // 60} minutes..."
            )
            response = await self._event_bus.rpc_request("request.network.gateway.status", request, timeout=30)
        except Exception as e:
            err_msg = f"An error occurred when requesting network gateway status list from Velocloud -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Got network gateway status list from Velocloud host {velocloud_host} "
                    f"for the past {lookup_interval // 60} minutes!"
                )
            else:
                environment = self._config.ENVIRONMENT_NAME.upper()
                err_msg = (
                    f"Error while retrieving network gateway status list from Velocloud in {environment} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
