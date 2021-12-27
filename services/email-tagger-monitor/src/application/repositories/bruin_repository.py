from shortuuid import uuid

from tenacity import retry, wait_exponential, stop_after_delay

from application.repositories import nats_error_response


class BruinRepository:

    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._timeout = self._config.MONITOR_CONFIG['nats_request_timeout']['post_email_tag_seconds']

    async def post_email_tag(self, email_id, tag_id):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def post_email_tag():
            err_msg = None
            self._logger.info(f'Sending tag "{tag_id}" for email_id: {email_id}')
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "email_id": email_id,
                    "tag_id": tag_id,
                }
            }
            try:
                response = await self._event_bus.rpc_request("bruin.email.tag.request", request_msg,
                                                             timeout=self._timeout)

            except Exception as e:
                err_msg = (
                    f'An error occurred when sending tags to Bruin API, '
                    f'with tags {tag_id} for email_id "{email_id}" -> {e}'
                )
                response = nats_error_response
            else:
                response_body = response['body']
                response_status = response['status']

                if response_status == 409:
                    self._logger.info(
                        f"Got 409 from Bruin. Tag already present for email_id {email_id} and tag_id {tag_id}")
                elif response_status not in range(200, 300):
                    err_msg = (
                        f'Error sending tags {tag_id} belonging to email {email_id} in '
                        f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(f'Tags for email {email_id} sent to Bruin')

            return response

        try:
            return await post_email_tag()
        except Exception as e:
            self._logger.error(f"Error sending tags {tag_id} to Bruin [email_id='{email_id}']: {e}")

    async def get_single_ticket_basic_info(self, ticket_id):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def get_single_ticket_basic_info():
            err_msg = None
            self._logger.info(f'Getting ticket "{ticket_id}" basic info')
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "ticket_id": ticket_id,
                }
            }
            try:
                response = await self._event_bus.rpc_request("bruin.single_ticket.basic.request", request_msg,
                                                             timeout=self._timeout)
            except Exception as err:
                err_msg = (
                    f'An error occurred when getting basic info from Bruin, '
                    f'for ticket_id "{ticket_id}" -> {err}'
                )
                response = nats_error_response
            else:
                response_body = response['body']
                response_status = response['status']

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error getting basic info for ticket {ticket_id} in '
                        f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
                else:
                    response['body'] = {
                        'ticket_id': ticket_id,
                        'ticket_status': response['body']['ticketStatus'],
                        'call_type': response['body']['callType'],
                        'category': response['body']['category'],
                        'creation_date': response['body']['createDate']
                    }

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(f'Basic info for ticket {ticket_id} retrieved from Bruin')

            return response

        try:
            return await get_single_ticket_basic_info()
        except Exception as e:
            self._logger.error(f"Error getting ticket {ticket_id} from Bruin: {e}")
