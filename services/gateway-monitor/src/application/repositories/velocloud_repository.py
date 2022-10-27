import json
import logging
from datetime import datetime, timedelta
from typing import Any

from shortuuid import uuid

logger = logging.getLogger(__name__)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


def get_data_from_response_message(message):
    return json.loads(message.data)


class VelocloudRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
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
            logger.info(f"Getting network gateway list from Velocloud host {velocloud_host}...")
            response = get_data_from_response_message(
                await self._nats_client.request("request.network.gateway.list", to_json_bytes(request), timeout=90)
            )
        except Exception as e:
            err_msg = f"An error occurred when requesting network gateway list from Velocloud -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(f"Got network gateway list from Velocloud host {velocloud_host}!")
            else:
                environment = self._config.ENVIRONMENT_NAME.upper()
                err_msg = (
                    f"Error while retrieving network gateway list from Velocloud in {environment} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_gateway_status_metrics(self, gateway: dict) -> dict:
        err_msg = None

        metrics = ["tunnelCount"]
        lookup_interval = self._config.MONITOR_CONFIG["gateway_metrics_lookup_interval"]
        start = datetime.now() - timedelta(seconds=lookup_interval)
        end = datetime.now()

        request = {
            "request_id": uuid(),
            "body": {
                "host": gateway["host"],
                "gateway_id": gateway["id"],
                "metrics": metrics,
                "interval": {"start": start.isoformat() + "Z", "end": end.isoformat() + "Z"},
            },
        }

        try:
            logger.info(
                f"Getting gateway status metrics from Velocloud host {gateway['host']} "
                f"for gateway {gateway['id']} for the past {lookup_interval // 60} minutes..."
            )
            response = get_data_from_response_message(
                await self._nats_client.request("request.gateway.status.metrics", to_json_bytes(request), timeout=90)
            )
        except Exception as e:
            err_msg = f"An error occurred when requesting gateway status metrics from Velocloud -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(
                    f"Got gateway status metrics from Velocloud host {gateway['host']} "
                    f"for gateway {gateway['id']} for the past {lookup_interval // 60} minutes!"
                )
            else:
                environment = self._config.ENVIRONMENT_NAME.upper()
                err_msg = (
                    f"Error while retrieving gateway status metrics from Velocloud in {environment} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
