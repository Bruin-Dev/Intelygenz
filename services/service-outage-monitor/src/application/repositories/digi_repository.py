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

    def get_digi_links(self, logical_id_list):
        digi_headers = ['00:04:2d', '00:27:04']
        digi_links = []
        for header in digi_headers:
            digi_link = [link for link in logical_id_list if header in link["logical_id"]]
            digi_links = digi_links + digi_link

        return digi_links

    def get_interface_name_from_digi_note(self, digi_note):
        if digi_note and digi_note.get('noteValue'):
            interface_name = None
            lines = digi_note.get('noteValue').splitlines()
            for line in lines:
                if line and len(line) > 0 and 'Interface: ' in line:
                    interface_name = ''.join(ch for ch in line)
                    break
            if interface_name is None or interface_name.strip() == '':
                return ''
            return interface_name.strip().replace('Interface: ', '')

        return ''