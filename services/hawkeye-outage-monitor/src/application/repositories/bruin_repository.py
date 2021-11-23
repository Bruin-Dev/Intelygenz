import os
from datetime import datetime
from shortuuid import uuid
from pytz import timezone

from application.repositories import nats_error_response


class BruinRepository:

    def __init__(self, config, logger, event_bus, notifications_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository

    async def get_tickets(self, client_id: int, ticket_topic: str, ticket_statuses: list, *,
                          service_number: str = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'client_id': client_id,
                'ticket_statuses': ticket_statuses,
                'ticket_topic': ticket_topic,
                'product_category': 'Network Scout',
            },
        }

        if service_number:
            request['body']['service_number'] = service_number

        try:
            if not service_number:
                self._logger.info(
                    f'Getting all tickets with any status of {ticket_statuses}, with ticket topic '
                    f'{ticket_topic} and belonging to client {client_id} from Bruin...'
                )
            else:
                self._logger.info(
                    f'Getting all tickets with any status of {ticket_statuses}, with ticket topic '
                    f'{ticket_topic}, service number {service_number} and belonging to client {client_id} from Bruin...'
                )

            response = await self._event_bus.rpc_request("bruin.ticket.basic.request", request, timeout=90)
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses}, '
                f'with ticket topic {ticket_topic} and belonging to client {client_id} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                if not service_number:
                    self._logger.info(
                        f'Got all tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic} and belonging to client {client_id} from Bruin!'
                    )
                else:
                    self._logger.info(
                        f'Got all tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic}, service number {service_number} and belonging to client '
                        f'{client_id} from Bruin!'
                    )
            else:
                if not service_number:
                    err_msg = (
                        f'Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic} and belonging to client {client_id} in '
                        f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
                else:
                    err_msg = (
                        f'Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic}, service number {service_number} and belonging to client {client_id} in '
                        f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

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
            response = await self._event_bus.rpc_request("bruin.ticket.details.request", request, timeout=15)
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
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def resolve_ticket(self, ticket_id: int, detail_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }

        try:
            self._logger.info(f'Resolving ticket {ticket_id} (affected detail ID: {detail_id})...')
            response = await self._event_bus.rpc_request("bruin.ticket.status.resolve", request, timeout=15)
            self._logger.info(f'Ticket {ticket_id} resolved!')
        except Exception as e:
            err_msg = f'An error occurred when resolving ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while resolving ticket {ticket_id} in {self._config.MONITOR_CONFIG["environment"].upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

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

            is_bruin_custom_status = response_status in (409, 471, 472, 473)
            if not (response_status in range(200, 300) or is_bruin_custom_status):
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
            watermark = "#*MetTel's IPA*#\nTriage (Ixia)\n\n"

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

    async def get_open_outage_tickets(self, client_id: int, *, service_number: str = None):
        ticket_statuses = ['New', 'InProgress', 'Draft']

        return await self.get_outage_tickets(client_id, ticket_statuses, service_number=service_number)

    async def get_outage_tickets(self, client_id: int, ticket_statuses: list, *, service_number: str = None):
        ticket_topic = 'VOO'

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses, service_number=service_number)

    async def append_autoresolve_note_to_ticket(self, ticket_id: int, serial_number: str):
        current_datetime_tz_aware = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        autoresolve_note = os.linesep.join([
            "#*MetTel's IPA*#",
            f'Auto-resolving detail for serial: {serial_number}',
            f'Real service status is UP.',
            f'Node to node status is UP.',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, autoresolve_note, service_numbers=[serial_number])

    async def __notify_error(self, err_msg):
        self._logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)

    async def open_ticket(self, ticket_id: int, detail_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }

        try:
            self._logger.info(f'Opening ticket {ticket_id} (affected detail ID: {detail_id})...')
            response = await self._event_bus.rpc_request("bruin.ticket.status.open", request, timeout=15)
            self._logger.info(f'Ticket {ticket_id} opened!')
        except Exception as e:
            err_msg = f'An error occurred when opening outage ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while opening outage ticket {ticket_id} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def unpause_ticket_detail(self, ticket_id: int, *, detail_id: int = None, service_number: str = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "ticket_id": ticket_id,
            },
        }

        if detail_id:
            request['body']['detail_id'] = detail_id

        if service_number:
            request['body']['service_number'] = service_number

        try:
            self._logger.info(f'Unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}...')
            response = await self._event_bus.rpc_request("bruin.ticket.unpause", request, timeout=30)
        except Exception as e:
            err_msg = (
                f'An error occurred when unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}. '
                f'Error: {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Detail {detail_id} (serial {service_number}) of ticket {ticket_id} was unpaused!')
            else:
                err_msg = (
                    f'Error while unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment. '
                    f'Error: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_reopening_note_to_ticket(self, ticket_id: int, service_number: str, affecting_causes: str):
        current_datetime_tz_aware = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        reopening_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'Re-opening detail for serial: {service_number}.',
            f'{affecting_causes}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, reopening_note, service_numbers=[service_number])
