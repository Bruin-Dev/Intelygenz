import math
import os
from datetime import datetime

from pytz import timezone
from shortuuid import uuid

from application.repositories import nats_error_response


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_tickets(self, client_id: int, ticket_topic: str, ticket_statuses: list, *,
                          service_number: str = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'client_id': client_id,
                'ticket_status': ticket_statuses,
                'ticket_topic': ticket_topic,
                'category': 'SD-WAN',
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

            response = await self._event_bus.rpc_request("bruin.ticket.request", request, timeout=90)
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
                        f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
                else:
                    err_msg = (
                        f'Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic}, service number {service_number} and belonging to client {client_id} in '
                        f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
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
                    f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

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
                    f'Error while appending note to ticket {ticket_id} in '
                    f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment. Note was {note}. Error: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_client_info(self, service_number: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'service_number': service_number,
            },
        }

        try:
            self._logger.info(f'Claiming client info for service number {service_number}...')
            response = await self._event_bus.rpc_request("bruin.customer.get.info", request, timeout=30)
            self._logger.info(f'Got client info for service number {service_number}!')
        except Exception as e:
            err_msg = (
                f'An error occurred when claiming client info for service number {service_number} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while claiming client info for service number {service_number} in '
                    f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_management_status(self, client_id: int, service_number: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "client_id": client_id,
                "service_number": service_number,
                "status": "A",
            },
        }

        try:
            self._logger.info(
                f'Claiming management status for service number {service_number} and client {client_id}...'
            )
            response = await self._event_bus.rpc_request("bruin.inventory.management.status", request, timeout=30)
            self._logger.info(f'Got management status for service number {service_number} and client {client_id}!')
        except Exception as e:
            err_msg = (
                f'An error occurred when claiming management status for service number {service_number} and '
                f'client {client_id} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while claiming management status for service number {service_number} and '
                    f'client {client_id} in {self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
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
                    f'Error while resolving ticket {ticket_id} in {self._config.TRIAGE_CONFIG["environment"].upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

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
                    f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
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
            self._logger.info(
                f'Creating outage ticket for device {service_number} that belongs to client {client_id}...')
            response = await self._event_bus.rpc_request("bruin.ticket.creation.outage.request", request, timeout=30)
            self._logger.info(f'Outage ticket for device {service_number} that belongs to client {client_id} created!')
        except Exception as e:
            err_msg = (
                f'An error occurred when creating outage ticket for device {service_number} belong to client'
                f'{client_id} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if not (response_status in range(200, 300) or response_status == 409 or response_status == 471):
                err_msg = (
                    f'Error while creating outage ticket for device {service_number} that belongs to client '
                    f'{client_id} in {self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_autoresolve_note_to_ticket(self, ticket_id: int, serial_number):
        current_datetime_tz_aware = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        autoresolve_note = os.linesep.join([
            '#*Automation Engine*#',
            f'Auto-resolving detail for serial: {serial_number}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, autoresolve_note)

    async def append_reopening_note_to_ticket(self, ticket_id: int, service_number: str, outage_causes: str):
        current_datetime_tz_aware = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        reopening_note = os.linesep.join([
            f'#*Automation Engine*#',
            f'Re-opening ticket.',
            f'{outage_causes}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, reopening_note, service_numbers=[service_number])

    async def get_outage_tickets(self, client_id: int, ticket_statuses: list, *, service_number: str = None):
        ticket_topic = 'VOO'

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses, service_number=service_number)

    async def get_open_outage_tickets(self, client_id: int, *, service_number: str = None):
        ticket_statuses = ['New', 'InProgress', 'Draft']

        return await self.get_outage_tickets(client_id, ticket_statuses, service_number=service_number)

    @staticmethod
    def is_management_status_active(management_status: str):
        return management_status in {"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"}

    async def append_triage_note(self, ticket_detail, ticket_note):
        ticket_id = ticket_detail['ticket_id']
        ticket_detail_id = ticket_detail['ticket_detail']['detailID']
        service_number = ticket_detail['ticket_detail']['detailValue']

        if self._config.TRIAGE_CONFIG['environment'] == 'dev':
            triage_message = (
                f'Triage note would have been appended to detail {ticket_detail_id} of ticket {ticket_id}'
                f'(serial: {service_number}). Note: {ticket_note}. Details at app.bruin.com/t/{ticket_id}'
            )
            self._logger.info(triage_message)
            await self._notifications_repository.send_slack_message(triage_message)
            return None
        elif self._config.TRIAGE_CONFIG['environment'] == 'production':
            if len(ticket_note) < 1500:

                append_note_response = await self.append_note_to_ticket(
                    ticket_id, ticket_note, service_numbers=[service_number]
                )

                if append_note_response['status'] == 503:
                    return 503

                if append_note_response['status'] not in range(200, 300):
                    return None
            else:
                lines = ticket_note.split('\n')
                accumulator = ""
                counter = 1
                total_notes = math.ceil(len(ticket_note) / 1000)

                for line in lines:
                    accumulator = accumulator + line + '\n'
                    is_last_index = lines.index(line) == (len(lines) - 1)
                    if len(accumulator) > 1000 or is_last_index:

                        note_page = f'Triage note: {counter}/{total_notes}'
                        accumulator = accumulator + note_page
                        append_note_response = await self.append_note_to_ticket(
                            ticket_id, accumulator, service_numbers=[service_number]
                        )
                        if append_note_response['status'] == 503:
                            return 503

                        if append_note_response['status'] not in range(200, 300):
                            return None
                        counter = counter + 1
                        accumulator = "#*Automation Engine*#\n" \
                                      "Triage\n"
            return 200
