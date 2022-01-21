from application.repositories import nats_error_response
from shortuuid import uuid


class DRIRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_dri_parameters(self, serial_number):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
             'serial_number': serial_number,
             'parameter_set': {
                            "ParameterNames": self._config.INTERMAPPER_CONFIG['dri_parameters'],
                            "Source": 0
                            }
            }
        }

        try:
            self._logger.info(f'Getting DRI parameters of serial number {serial_number}')
            response = await self._event_bus.rpc_request("dri.parameters.request", request, timeout=120)
        except Exception as e:
            err_msg = (
                f'An error occurred while getting DRI parameter for serial number {serial_number}. '
                f'Error: {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Got DRI parameter of serial number {serial_number}!')
            else:
                err_msg = (
                    f'Error while getting DRI parameter of serial number {serial_number} in '
                    f'{self._config.INTERMAPPER_CONFIG["environment"].upper()} environment. Error: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
