from application.repositories import nats_error_response
from shortuuid import uuid
from tenacity import retry, stop_after_delay, wait_exponential


class EmailTaggerRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._timeout = self._config.MONITOR_CONFIG["nats_request_timeout"]["kre_seconds"]

    async def get_prediction(self, email_data: dict):
        email_id = email_data["email"]["email_id"]

        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def get_prediction():
            err_msg = None

            self._logger.info(f"Sending email data to get prediction: {email_id}")
            request_msg = {"request_id": uuid(), "body": email_data}
            try:
                response = await self._event_bus.rpc_request(
                    "email_tagger.prediction.request", request_msg, timeout=self._timeout
                )

            except Exception as e:
                err_msg = f"An error occurred when sending emails to Email Tagger for email_id '{email_id}' -> {e}"
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while getting prediction for email "{email_id}" in '
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(f"Prediction request sent for email {email_id} to Email Tagger")

            return response

        try:
            return await get_prediction()
        except Exception as e:
            self._logger.error(f"Error trying to get tag prediction from KRE [email_id='{email_id}']: {e}")

    async def save_metrics(self, email_data: dict, ticket_data: dict):
        email_id = email_data["email"]["email_id"]
        ticket_id = ticket_data["ticket_id"]

        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def save_metrics():
            err_msg = None
            self._logger.info(f"Sending email and ticket data to save_metrics: {email_id}")
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "original_email": email_data,
                    "ticket": ticket_data,
                },
            }
            try:
                response = await self._event_bus.rpc_request(
                    "email_tagger.metrics.request", request_msg, timeout=self._timeout
                )

            except Exception as e:
                err_msg = f"An error occurred when sending emails to Email Tagger for email_id '{email_id}' -> {e}"
                response = nats_error_response
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while saving metrics for email "{email_id}" in '
                        f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(
                    f"SaveMetrics request sent for email {email_id} and ticket {ticket_id} to Email Tagger"
                )

            return response

        try:
            return await save_metrics()
        except Exception as e:
            self._logger.error(
                f"Error trying to send metrics to KRE [email_id='{email_id}', ticket_id='{ticket_id}']: {e}"
            )
