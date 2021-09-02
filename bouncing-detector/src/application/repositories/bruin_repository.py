import os
import re
from datetime import datetime

from application.repositories import nats_error_response
from dateutil.parser import parse
from pytz import timezone
from shortuuid import uuid


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_affecting_ticket(self, client_id, serial):
        ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved']
        ticket_request_msg = {
            'request_id': uuid(),
            'body': {
                'client_id': client_id,
                'product_category': 'SD-WAN',
                'ticket_topic': 'VAS',
                'service_number': serial,
                'ticket_statuses': ticket_statuses
            }
        }
        self._logger.info(f"Retrieving affecting tickets for serial: {serial}")
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.basic.request",
                                                        ticket_request_msg,
                                                        timeout=90)
        if all_tickets['status'] not in range(200, 300):
            self._logger.error(f"Error: an error occurred retrieving affecting tickets by serial")
            return None

        if len(all_tickets['body']) > 0:
            all_tickets_sorted = sorted(all_tickets['body'], key=lambda item: parse(item["createDate"]), reverse=True)
            ticket_id = all_tickets_sorted[0]['ticketID']
            ticket_details = await self.get_ticket_details(ticket_id)

            if ticket_details['status'] not in range(200, 300):
                self._logger.error(f"Error: an error occurred retrieving ticket details for ticket: {ticket_id}")
                return None

            ticket_details_body = ticket_details['body']
            self._logger.info(f'Returning ticket details of ticket: {ticket_id}')
            return {
                'ticketID': ticket_id,
                **ticket_details_body,
            }
        self._logger.info(f'No service affecting tickets found for serial: {serial}')
        return {}

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
        except Exception as e:
            err_msg = f'An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving details of ticket {ticket_id} in '
                    f'{self._config.BOUNCING_DETECTOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f'Got details of ticket {ticket_id} from Bruin!')

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
            self._logger.info(f'Appending note to ticket {ticket_id}... Note contents: {note}')
            response = await self._event_bus.rpc_request("bruin.ticket.note.append.request", request, timeout=15)
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
                    f'Error while appending note to ticket {ticket_id} in '
                    f'{self._config.BOUNCING_DETECTOR_CONFIG["environment"].upper()} \
                    environment. Note was {note}. Error: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_affecting_ticket(self, client_id: int, service_number: str, contact_info: dict):
        err_msg = None
        ticket_details = {
            "request_id": uuid(),
            "body": {
                "clientId": client_id,
                "category": "VAS",
                "services": [
                    {
                        "serviceNumber": service_number
                    }
                ],
                "contacts": [
                    {
                        "email": contact_info['site']['email'],
                        "phone": contact_info['site']['phone'],
                        "name": contact_info['site']['name'],
                        "type": "site"
                    },
                    {
                        "email": contact_info['ticket']['email'],
                        "phone": contact_info['ticket']['phone'],
                        "name": contact_info['ticket']['name'],
                        "type": "ticket"
                    }
                ]
            }
        }

        try:
            self._logger.info(
                f'Creating affecting ticket for serial {service_number} belonging to client {client_id}...')

            response = await self._event_bus.rpc_request("bruin.ticket.creation.request",
                                                         ticket_details, timeout=90)

        except Exception as e:
            err_msg = (
                f'An error occurred while creating affecting ticket for client id {client_id} and serial '
                f'{service_number} -> {e}')
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Affecting ticket for client {client_id} and serial {service_number} created successfully!')
            else:
                err_msg = (
                    f'Error while opening affecting ticket for client {client_id} and serial {service_number} in '
                    f'{self._config.BOUNCING_DETECTOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
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
                    f'{self._config.BOUNCING_DETECTOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_reopening_note_to_ticket(self, ticket_id: int, affecting_causes: str):
        current_datetime_tz_aware = datetime.now(timezone(self._config.BOUNCING_DETECTOR_CONFIG['timezone']))
        reopening_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'Re-opening ticket.',
            f'{affecting_causes}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, reopening_note)

    @staticmethod
    def find_detail_by_serial(ticket, edge_serial_number):
        ticket_details = None
        for detail in ticket.get("ticketDetails"):
            if edge_serial_number == detail['detailValue']:
                ticket_details = detail
                break
        return ticket_details
