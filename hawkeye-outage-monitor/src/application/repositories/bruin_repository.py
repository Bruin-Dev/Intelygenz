from shortuuid import uuid

from application.repositories import nats_error_response


class BruinRepository:

    def __init__(self, config, logger, event_bus, notifications_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository

    async def create_outage_ticket(self, client_id: int, service_number: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "client_id": client_id,
                "service_number": service_number,
            },
        }

        try:
            self._logger.info(f'Creating outage ticket for device {service_number} belonging to client {client_id}...')
            response = await self._event_bus.rpc_request("bruin.ticket.creation.outage.request", request, timeout=30)
        except Exception as e:
            err_msg = (
                f'An error occurred when creating outage ticket for device {service_number} belonging to client'
                f'{client_id} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if not (response_status in range(200, 300) or response_status == 409 or response_status == 471):
                err_msg = (
                    f'Error while creating outage ticket for device {service_number} that belongs to client '
                    f'{client_id}: Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f'Outage ticket for device {service_number} belonging to client {client_id} created!')

        if err_msg:
            await self.__notify_error(err_msg)

        return response

    async def append_note_to_ticket(self, ticket_id: int, note: str, *, service_numbers: list = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': note,
            },
        }

        if service_numbers:
            request['body']['service_numbers'] = service_numbers

        try:
            if service_numbers:
                self._logger.info(
                    f'Appending note for service number(s) {", ".join(service_numbers)} in ticket {ticket_id}...'
                )
            else:
                self._logger.info(f'Appending note for all service number(s) in ticket {ticket_id}...')

            response = await self._event_bus.rpc_request("bruin.ticket.note.append.request", request, timeout=15)
        except Exception as e:
            err_msg = (
                f'An error occurred when appending a ticket note to ticket {ticket_id}. '
                f'Ticket note: {note}. Error: {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while appending note to ticket {ticket_id}: Error: '
                    f'Error {response_status} - {response_body}'
                )
            else:
                if service_numbers:
                    self._logger.info(
                        f'Note for service number(s) {", ".join(service_numbers)} appended to ticket {ticket_id}!'
                    )
                else:
                    self._logger.info(f'Note for all service number(s) appended to ticket {ticket_id}!')

        if err_msg:
            await self.__notify_error(err_msg)

        return response

    async def append_triage_note_to_ticket(self, ticket_id: int, service_number: str, note: str):
        if len(note) < 1500:
            return await self.append_note_to_ticket(ticket_id, note, service_numbers=[service_number])
        else:
            watermark = '#*Automation Engine*#\nTriage (Ixia)\n\n'

            # Let's remove the watermark to ease chunking the note
            note = note.replace(watermark, '')

            total_notes = (len(note) // 1000) + 1
            notes_footer = '\n\nTriage note: {{current_note_number}}/{total_notes}'.format(total_notes=total_notes)

            current_note_number = 1
            current_note = ""

            lines = note.splitlines()
            for index, line in enumerate(lines):
                current_note += f'{line}\n'
                is_last_index = index == len(lines) - 1

                if len(current_note) > 1000 or is_last_index:
                    current_footer = notes_footer.format(current_note_number=current_note_number)
                    current_note = watermark + current_note + current_footer

                    append_note_response = await self.append_note_to_ticket(
                        ticket_id, current_note, service_numbers=[service_number]
                    )

                    if append_note_response['status'] not in range(200, 300):
                        return append_note_response

                    current_note_number += 1
                    current_note = ""

            return {
                'body': f'Triage note split into {total_notes} chunks and appended successfully!',
                'status': 200,
            }

    async def __notify_error(self, err_msg):
        self._logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)
