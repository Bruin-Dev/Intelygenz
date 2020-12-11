from typing import List

from shortuuid import uuid

from application import nats_error_response


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
                'ticket_status': ticket_statuses,
                'ticket_topic': ticket_topic,
                'category': 'Network Scout',
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
            else:
                self._logger.info(f'Got details of ticket {ticket_id} from Bruin!')

        if err_msg:
            await self.__notify_error(err_msg)

        return response

    async def create_affecting_ticket(self, client_id: int, service_number: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "clientId": client_id,
                "services": [
                    {
                        "serviceNumber": service_number,
                    },
                ],
                "category": "VAS",
                # TODO: Remove these hardcoded contacts
                'contacts': [
                    {
                        "email": 'ndimuro@mettel.net',
                        "phone": '9876543210',
                        "name": 'Nicholas DiMuro',
                        "type": "site",
                    },
                    {
                        "email": 'ndimuro@mettel.net',
                        "phone": '9876543210',
                        "name": 'Nicholas DiMuro',
                        "type": "ticket",
                    },
                ],
            },
        }

        try:
            self._logger.info(
                f'Creating affecting ticket for device {service_number} belonging to client {client_id}...'
            )
            response = await self._event_bus.rpc_request("bruin.ticket.creation.request", request, timeout=30)
        except Exception as e:
            err_msg = (
                f'An error occurred when creating affecting ticket for device {service_number} belonging to client '
                f'{client_id} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while creating affecting ticket for device {service_number} that belongs to client '
                    f'{client_id}: Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(
                    f'Affecting ticket for device {service_number} belonging to client {client_id} created!'
                )

        if err_msg:
            await self.__notify_error(err_msg)

        return response

    async def append_multiple_notes_to_ticket(self, ticket_id: int, notes: List[dict]):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        try:
            self._logger.info(f'Posting multiple notes to ticket {ticket_id}...')
            response = await self._event_bus.rpc_request(
                "bruin.ticket.multiple.notes.append.request", request, timeout=45
            )
        except Exception as e:
            err_msg = (
                f'An error occurred when appending multiple ticket notes to ticket {ticket_id}. '
                f'Notes: {notes}. Error: {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while appending multiple notes to ticket {ticket_id} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment. '
                    f'Notes were {notes}. Error: Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f'Posted multiple notes to ticket {ticket_id}!')

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_affecting_tickets(self, client_id: int, ticket_statuses: list, *, service_number: str = None):
        ticket_topic = 'VAS'

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses, service_number=service_number)

    async def get_open_affecting_tickets(self, client_id: int, *, service_number: str = None):
        ticket_statuses = ['New', 'InProgress', 'Draft']

        return await self.get_affecting_tickets(client_id, ticket_statuses, service_number=service_number)

    async def __notify_error(self, err_msg):
        self._logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)
