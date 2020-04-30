from shortuuid import uuid

from application.repositories import nats_error_response


class T7Repository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_prediction(self, ticket_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
            },
        }

        try:
            self._logger.info(f'Claiming T7 prediction for ticket {ticket_id}...')
            response = await self._event_bus.rpc_request("t7.prediction.request", request, timeout=60)
            self._logger.info(f'Got T7 prediction for ticket {ticket_id}!')
        except Exception as e:
            err_msg = f'An error occurred when claiming T7 prediction for ticket {ticket_id}. Error: {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while claiming T7 prediction for ticket {ticket_id} in {self._config.ENVIRONMENT.upper()} '
                    f'environment. Error: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
