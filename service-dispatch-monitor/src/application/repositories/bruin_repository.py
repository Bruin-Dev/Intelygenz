import iso8601
from shortuuid import uuid
import re

from application.repositories import nats_error_response


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    @staticmethod
    def is_valid_ticket_id(ticket_id):
        # Check ticket id format for example: '4663397|IW24654081'
        # Bruin ticket ID like 712637/IW76236 and 123-3123 are likely to be from other
        # kind of tickets (like new installations), thus other teams that are not his,
        # 4485610(Order)/4520284(Port)
        # Store #1234
        # PON 1234
        # Discard All with more than one ticket
        if re.match("[0-9]+$", ticket_id):
            return True
        else:
            return False

    async def get_ticket_details(self, ticket_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id
            },
        }

        try:
            self._logger.info(f'Getting details of ticket {ticket_id} from Bruin...')
            response = await self._event_bus.rpc_request("bruin.ticket.details.request", request, timeout=60)
            self._logger.info(f'Got details of ticket {ticket_id} from Bruin!')
        except Exception as e:
            err_msg = f'An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving details of ticket {ticket_id} in '
                    f'{self._config.ENVIRONMENT.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_note_to_ticket(self, ticket_id: int, note: str, is_private: bool = False):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': note,
                'is_private': is_private,
            },
        }

        try:
            if is_private:
                self._logger.info(f'Appending private note to ticket {ticket_id}... Note contents: {note}')
            else:
                self._logger.info(f'Appending note to ticket {ticket_id}... Note contents: {note}')

            response = await self._event_bus.rpc_request("bruin.ticket.note.append.request", request, timeout=60)
            self._logger.info(f'Note appended to ticket {ticket_id}!')
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
                    f'Error while appending note to ticket {ticket_id} in {self._config.ENVIRONMENT.upper()} '
                    f'environment. Note was {note}. Error: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    @staticmethod
    def sort_ticket_notes_by_created_date(ticket_notes):
        ticket_notes = [tn for tn in ticket_notes if tn if 'noteValue' in tn if tn.get('noteValue')]
        ticket_notes = sorted(ticket_notes, key=lambda tn: iso8601.parse_date(tn.get('createdDate')))
        return ticket_notes
