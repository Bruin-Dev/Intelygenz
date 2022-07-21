import os
from datetime import datetime

from pytz import timezone
from shortuuid import uuid


class ServiceNowRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    @staticmethod
    def _build_incident_summary(gateway: dict) -> str:
        return f"{gateway['name']}: Medium: VCG Tunnel Count Threshold Violation"

    def _build_incident_note(self, gateway: dict) -> str:
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        lookup_interval = self._config.MONITOR_CONFIG["gateway_metrics_lookup_interval"]
        tunnel_count_threshold = self._config.MONITOR_CONFIG["thresholds"]["tunnel_count"]
        tunnel_count = gateway["metrics"]["tunnelCount"]

        note_lines = [
            f"VCO: {gateway['host']}",
            f"VCG: {gateway['name']}",
            "",
            f"Condition: Over {tunnel_count_threshold}% reduction in tunnel count compared to average",
            f"Minimum Tunnel Count: {tunnel_count['min']}",
            f"Average Tunnel Count: {tunnel_count['average']}",
            f"Scan Interval: {lookup_interval // 60} minutes",
            "",
            f"Link: https://{gateway['host']}/#!/operator/admin/gateways/{gateway['id']}/monitor/",
            "",
            f"TimeStamp: {current_datetime_tz_aware}",
        ]

        return os.linesep.join(note_lines)

    async def report_incident(self, gateway: dict):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "host": gateway["host"],
                "gateway": gateway["name"],
                "summary": self._build_incident_summary(gateway),
                "note": self._build_incident_note(gateway),
            },
        }

        try:
            self._logger.info(
                f"Reporting incident to ServiceNow for host {gateway['host']} and gateway {gateway['name']}..."
            )
            response = await self._event_bus.rpc_request("servicenow.incident.report.request", request, timeout=30)
        except Exception as e:
            err_msg = f"An error occurred when reporting incident to ServiceNow -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Reported incident to ServiceNow for host {gateway['host']} and gateway {gateway['name']}!"
                )
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
