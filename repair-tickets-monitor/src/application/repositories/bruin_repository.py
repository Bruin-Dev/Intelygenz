from shortuuid import uuid

from tenacity import retry, wait_exponential, stop_after_delay

from application.repositories import nats_error_response


class BruinRepository:

    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._timeout = self._config.MONITOR_CONFIG['nats_request_timeout']['post_ticket_seconds']

    async def get_site(self, client_id, site_id):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def get_site():
            err_msg = None
            self._logger.info(f'Getting site for client_id "{client_id}" and site_id "{site_id}')
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "client_id": client_id,
                    "site_id": site_id,
                }
            }
            try:
                response = await self._event_bus.rpc_request("bruin.get.site", request_msg, timeout=self._timeout)
            except Exception as err:
                err_msg = (
                    f'An error occurred when getting site from Bruin, '
                    f'for client_id "{client_id}" and site_id "{site_id}" -> {err}'
                )
                response = nats_error_response
            else:
                response_body = response['body']
                response_status = response['status']

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error getting basic info for client_id "{client_id}" and site_id "{site_id}" in '
                        f'{self._config.ENVIRONMENT.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
                else:
                    # TODO: review - return as array or just the first element or none if empty
                    response['body'] = {
                        'site': response['body'].get('documents', [])
                    }

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(f'Site for client_id "{client_id}" and site_id "{site_id}" retrieved from Bruin')

            return response

        try:
            return await get_site()
        except Exception as e:
            self._logger.error(f'Error getting client_id "{client_id}" and site_id "{site_id}" from Bruin: {e}')
