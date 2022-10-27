import json
import logging
import os
from datetime import datetime
from typing import Any, List

from pytz import timezone
from shortuuid import uuid

from application import Troubles

logger = logging.getLogger(__name__)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


def get_data_from_response_message(message):
    return json.loads(message.data)


class ServiceNowRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    @staticmethod
    def _build_incident_summary(gateway: dict) -> str:
        if gateway["trouble"] == Troubles.OFFLINE:
            return f"{gateway['name']}: VCG Offline"

        if gateway["trouble"] == Troubles.TUNNEL_COUNT:
            return f"{gateway['name']}: VCG Tunnel Count Threshold Violation"

    def _build_incident_note(self, gateway: dict) -> str:
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        trouble_note_lines = self._get_trouble_note_lines(gateway)

        note_lines = [
            f"VCO: {gateway['host']}",
            f"VCG: {gateway['name']}",
            "",
            *trouble_note_lines,
            "",
            f"TimeStamp: {current_datetime_tz_aware}",
        ]

        return os.linesep.join(note_lines)

    def _get_trouble_note_lines(self, gateway: dict) -> List[str]:
        if gateway["trouble"] == Troubles.OFFLINE:
            return ["Condition: Gateway is offline"]

        if gateway["trouble"] == Troubles.TUNNEL_COUNT:
            lookup_interval = self._config.MONITOR_CONFIG["gateway_metrics_lookup_interval"]
            tunnel_count_threshold = self._config.MONITOR_CONFIG["thresholds"][Troubles.TUNNEL_COUNT]
            tunnel_count = gateway["metrics"]["tunnelCount"]

            return [
                f"Condition: Over {tunnel_count_threshold}% reduction in tunnel count compared to average",
                f"Minimum Tunnel Count: {tunnel_count['min']}",
                f"Average Tunnel Count: {tunnel_count['average']}",
                f"Scan Interval: {lookup_interval // 60} minutes",
            ]

    @staticmethod
    def _build_incident_link(gateway: dict) -> str:
        return f"https://{gateway['host']}/#!/operator/admin/gateways/{gateway['id']}/monitor/"

    async def report_incident(self, gateway: dict):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "host": gateway["host"],
                "gateway": gateway["name"],
                "summary": self._build_incident_summary(gateway),
                "note": self._build_incident_note(gateway),
                "link": self._build_incident_link(gateway),
            },
        }

        try:
            logger.info(
                f"Reporting {gateway['trouble'].value} incident to ServiceNow "
                f"for host {gateway['host']} and gateway {gateway['name']}..."
            )
            response = get_data_from_response_message(
                await self._nats_client.request(
                    "servicenow.incident.report.request", to_json_bytes(request), timeout=90
                )
            )
        except Exception as e:
            err_msg = f"An error occurred when reporting incident to ServiceNow -> {e}"
            response = {"body": None, "status": 503}
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                logger.info(
                    f"Reported {gateway['trouble'].value} incident to ServiceNow "
                    f"for host {gateway['host']} and gateway {gateway['name']}!"
                )
            else:
                environment = self._config.ENVIRONMENT_NAME.upper()
                err_msg = (
                    f"Failed to report {gateway['trouble'].value} incident to ServiceNow "
                    f"for host {gateway['host']} and gateway {gateway['name']} in {environment} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
