from shortuuid import uuid
from application.repositories import nats_error_response


class DiGiRepository:

    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def reboot_link(self, serial_number, ticket_id, logical_id):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'velo_serial': serial_number,
                'ticket': str(ticket_id),
                'MAC': logical_id
            },
        }

        try:
            self._logger.info(f'Rebooting DiGi link of ticket {ticket_id} from Bruin...')
            response = await self._event_bus.rpc_request("digi.reboot", request, timeout=90)
            self._logger.info(f'Got details of ticket {ticket_id} from Bruin!')
        except Exception as e:
            err_msg = f'An error occurred when attempting a DiGi reboot for ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while attempting a DiGi reboot for ticket {ticket_id} in '
                    f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
