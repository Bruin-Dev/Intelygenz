import json
import logging
from datetime import datetime, timedelta

from shortuuid import uuid

from application import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class HawkeyeRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_tests_results(self, *, probe_uids: list, interval: dict) -> dict:
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "probe_uids": probe_uids,
                "interval": interval,
            },
        }

        try:
            logger.info(f"Getting tests results for {len(probe_uids)} probes from Hawkeye...")
            response = await self._nats_client.request("hawkeye.test.request", to_json_bytes(request), timeout=60)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred when requesting tests results from Hawkeye -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = f"Error while retrieving tests results: Error {response_status} - {response_body}"
            else:
                logger.info(f"Got all tests results for {len(probe_uids)} probes from Hawkeye!")

        if err_msg:
            await self.__notify_error(err_msg)

        return response

    async def get_tests_results_for_affecting_monitoring(self, probe_uids: list) -> dict:
        now = datetime.utcnow()
        past_moment = now - timedelta(seconds=self._config.MONITOR_CONFIG["scan_interval"])

        scan_interval = {
            "start": past_moment,
            "end": now,
        }
        return await self.get_tests_results(probe_uids=probe_uids, interval=scan_interval)

    async def __notify_error(self, err_msg):
        logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)
