import json
import logging

from shortuuid import uuid
from tenacity import retry, stop_after_attempt, wait_exponential

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class DRIRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_dri_parameters(self, serial_number):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.INTERMAPPER_CONFIG["wait_multiplier"],
                min=self._config.INTERMAPPER_CONFIG["wait_min"],
                max=self._config.INTERMAPPER_CONFIG["wait_max"],
            ),
            stop=stop_after_attempt(self._config.INTERMAPPER_CONFIG["stop_after_attempt"]),
            reraise=True,
        )
        async def get_dri_parameters():
            err_msg = None

            request = {
                "request_id": uuid(),
                "body": {
                    "serial_number": serial_number,
                    "parameter_set": {"ParameterNames": self._config.INTERMAPPER_CONFIG["dri_parameters"], "Source": 0},
                },
            }

            try:
                logger.info(f"Getting DRI parameters of serial number {serial_number}")
                response = await self._nats_client.request(
                    "dri.parameters.request", to_json_bytes(request), timeout=120
                )
                response = json.loads(response.data)
            except Exception as e:
                err_msg = f"An error occurred while getting DRI parameter for serial number {serial_number}. Error: {e}"
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status in range(200, 300):
                    logger.info(f"Got DRI parameter of serial number {serial_number}!")
                else:
                    err_msg = (
                        f"Error while getting DRI parameter of serial number {serial_number} in "
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment. Error: "
                        f"Error {response_status} - {response_body}"
                    )
                if response_status == 204:
                    logger.info(response_body)
                    raise Exception(f"Error: {response_body}")

            if err_msg:
                logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)

            return response

        try:
            return await get_dri_parameters()
        except Exception as e:
            msg = f"Max retries reached when getting dri parameters - exception: {e}"
            logger.error(msg)
            await self._notifications_repository.send_slack_message(msg)
            return {"body": msg, "status": 400}
