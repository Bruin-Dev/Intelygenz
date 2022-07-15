from datetime import datetime, timedelta

from shortuuid import uuid


class VelocloudRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_network_gateway_list(self, velocloud_host: str) -> dict:
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "host": velocloud_host,
            },
        }

        try:
            self._logger.info(f"Getting network gateway list from Velocloud host {velocloud_host}...")
            response = await self._event_bus.rpc_request("request.network.gateway.list", request, timeout=30)
        except Exception as e:
            err_msg = f"An error occurred when requesting network gateway list from Velocloud -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Got network gateway list from Velocloud host {velocloud_host}!")
            else:
                environment = self._config.ENVIRONMENT_NAME.upper()
                err_msg = (
                    f"Error while retrieving network gateway list from Velocloud in {environment} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_gateway_status_metrics(self, velocloud_host: str, gateway_id: int) -> dict:
        err_msg = None

        metrics = ["tunnelCount"]
        lookup_interval = self._config.MONITOR_CONFIG["gateway_metrics_lookup_interval"]
        start = datetime.now() - timedelta(seconds=lookup_interval)
        end = datetime.now()

        request = {
            "request_id": uuid(),
            "body": {
                "host": velocloud_host,
                "gateway_id": gateway_id,
                "metrics": metrics,
                "interval": {"start": start.isoformat() + "Z", "end": end.isoformat() + "Z"},
            },
        }

        try:
            self._logger.info(
                f"Getting gateway status metrics from Velocloud host {velocloud_host} "
                f"for gateway {gateway_id} for the past {lookup_interval // 60} minutes..."
            )
            response = await self._event_bus.rpc_request("request.gateway.status.metrics", request, timeout=30)
        except Exception as e:
            err_msg = f"An error occurred when requesting gateway status metrics from Velocloud -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Got gateway status metrics from Velocloud host {velocloud_host} "
                    f"for gateway {gateway_id} for the past {lookup_interval // 60} minutes!"
                )
            else:
                environment = self._config.ENVIRONMENT_NAME.upper()
                err_msg = (
                    f"Error while retrieving gateway status metrics from Velocloud in {environment} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
