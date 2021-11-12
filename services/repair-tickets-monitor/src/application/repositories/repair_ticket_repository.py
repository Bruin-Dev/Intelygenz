from shortuuid import uuid

from tenacity import retry, wait_exponential, stop_after_delay

from application.repositories import nats_error_response


class RepairTicketRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._timeout = self._config.MONITOR_CONFIG['nats_request_timeout']['kre_seconds']

    async def save_created_ticket_feedback(self, email_data: dict):
        email_id = email_data['email']['email_id']

        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def save_created_ticket_feedback():
            err_msg = None

            self._logger.info(f"Sending email data to get prediction: {email_id}")
            request_msg = {
                "request_id": uuid(),
                "body": email_data
            }
            try:
                response = await self._event_bus.rpc_request("repair_ticket.save_create_ticket.request", request_msg,
                                                             timeout=self._timeout)

            except Exception as e:
                err_msg = f"An error occurred when sending emails to RTA for email_id '{email_id}' -> {e}"
                response = nats_error_response
            else:
                response_body = response['body']
                response_status = response['status']

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error while getting prediction for email "{email_id}" in '
                        f'{self._config.ENVIRONMENT.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(f'Prediction request sent for email {email_id} to RTA')

            return response

        try:
            return await save_created_ticket_feedback()
        except Exception as e:
            self._logger.error(f"Error trying to get tag prediction from KRE [email_id='{email_id}']: {e}")
