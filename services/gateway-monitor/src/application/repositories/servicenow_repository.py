import os
from datetime import datetime
from typing import Tuple

from pytz import timezone
from shortuuid import uuid


class ServiceNowRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    @staticmethod
    def _build_incident_summary(gateway_name: str):
        return f"{gateway_name}: Medium: VGC Tunnel Count Threshold Violation"

    def _build_incident_note(self, host: str, gateway_name: str, gateway_pair: Tuple[dict, dict]):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        tunnel_count_threshold = self._config.MONITOR_CONFIG["thresholds"]["tunnel_count"]

        note_lines = [
            f"Host Name: {host}",
            f"VGC: {gateway_name}",
            "",
            f"Condition: {tunnel_count_threshold}% reduction in tunnel count compared to average",
            f"Current Tunnel Count: {gateway_pair[1]['tunnelCount']}",
            f"Average Tunnel Count: {gateway_pair[0]['tunnelCount']}",
            "",
            f"TimeStamp: {current_datetime_tz_aware}",
        ]

        return os.linesep.join(note_lines)

    async def report_incident(self, host: str, gateway_name: str, gateway_pair: Tuple[dict, dict]):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "host": host,
                "gateway": gateway_name,
                "summary": self._build_incident_summary(gateway_name),
                "note": self._build_incident_note(host, gateway_name, gateway_pair),
            },
        }

        try:
            self._logger.info(f"Reporting incident to ServiceNow for host {host} and gateway {gateway_name}...")
            response = await self._event_bus.rpc_request("servicenow.incident.report.request", request, timeout=30)
        except Exception as e:
            err_msg = f"An error occurred when reporting incident to ServiceNow -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Reported incident to ServiceNow for host {host} and gateway {gateway_name}!")
            else:
                environment = self._config.ENVIRONMENT_NAME.upper()
                err_msg = (
                    f"Error while reporting incident to ServiceNow in {environment} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
