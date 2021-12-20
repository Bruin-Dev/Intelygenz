from shortuuid import uuid

import humps
from tenacity import retry, wait_exponential, stop_after_delay

from application.repositories import nats_error_response
from typing import Any, Dict, List


class BruinRepository:

    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._timeout = self._config.MONITOR_CONFIG['nats_request_timeout']['bruin_request_seconds']

    async def get_single_ticket_basic_info(self, ticket_id):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG['multiplier'],
                min=self._config.NATS_CONFIG['min']
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay'])
        )
        async def get_single_ticket_basic_info():
            err_msg = None
            self._logger.info(f'Getting ticket "{ticket_id}" basic info')
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "ticket_id": ticket_id,
                }
            }
            try:
                response = await self._event_bus.rpc_request(
                    "bruin.single_ticket.basic.request",
                    request_msg,
                    timeout=self._timeout
                )

            except Exception as err:
                err_msg = (
                    f'An error occurred when getting basic info from Bruin, '
                    f'for ticket_id "{ticket_id}" -> {err}'
                )
                response = nats_error_response
            else:
                response_body = response['body']
                response_status = response['status']

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error getting basic info for ticket {ticket_id} in '
                        f'{self._config.ENVIRONMENT.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
                else:
                    response['body'] = {
                        'ticket_id': ticket_id,
                        'ticket_status': response['body']['ticketStatus'],
                        'call_type': response['body']['callType'],
                        'category': response['body']['category'],
                        'creation_date': response['body']['createDate']
                    }

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(f'Basic info for ticket {ticket_id} retrieved from Bruin')

            return response

        try:
            return await get_single_ticket_basic_info()
        except Exception as e:
            self._logger.error(f"Error getting ticket {ticket_id} from Bruin: {e}")

    async def get_single_ticket_info_with_service_numbers(self, ticket_id):
        basic_info_response = await self.get_single_ticket_basic_info(ticket_id)
        if basic_info_response['status'] not in range(200, 300):
            return {'status': basic_info_response['status'], 'body': 'Error while retrieving basic ticket info'}
        if not basic_info_response['body']:
            return {'status': 404, 'body': 'Ticket not found'}

        ticket = basic_info_response['body']
        details = await self.get_ticket_details(ticket['ticket_id'])
        if details['status'] not in range(200, 300):
            err_msg = f'Error while retrieving details from ticket {ticket_id}'
            self._logger(err_msg)
            self._notifications_repository.send_slack_message(err_msg)
            return {'status': 500, 'body': 'Error while retrieving ticket service_numbers'}
        service_numbers = self._get_details_service_numbers(details['body'])
        ticket['service_numbers'] = service_numbers

        return {'status': 200, 'body': ticket}

    async def verify_service_number_information(self, client_id, service_number):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG['multiplier'],
                min=self._config.NATS_CONFIG['min']
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay'])
        )
        async def verify_service_number_information():
            err_msg = None
            self._logger.info(f'Getting inventory "{client_id}" and service number {service_number}')
            request_msg = {
                "request_id": uuid(),
                "body": {
                    "client_id": client_id,
                    "service_number": service_number,
                    "status": "A",
                }
            }
            try:
                response = await self._event_bus.rpc_request(
                    "bruin.customer.get.info",
                    request_msg,
                    timeout=self._timeout
                )
            except Exception as err:
                err_msg = (
                    f'An error occurred when getting service number info from Bruin, '
                    f'for ticket_id "{client_id}" -> {err}'
                )
                response = nats_error_response
            else:
                response_body = response['body']
                response_status = response['status']

                if response_status not in range(200, 300):
                    err_msg = (
                        f'Error getting service number info for {service_number} in '
                        f'{self._config.ENVIRONMENT.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
                elif not response_body:
                    self._logger.info(f'Service number not validated {service_number}')
                    response['status'] = 404
                    response['body'] = "Service number not validated"
                else:
                    response['status'] = response_status
                    response['body'] = {
                        'client_id': client_id,
                        'site_id': response_body[0].get('site_id'),
                        'service_number': service_number,
                    }

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            else:
                self._logger.info(f'Service number info {service_number} retrieved from Bruin')

            return response

        try:
            return await verify_service_number_information()
        except Exception as e:
            self._logger.error(f"Error getting service number info {service_number} from Bruin: {e}")

    async def get_ticket_details(self, ticket_id: int):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG['multiplier'],
                min=self._config.NATS_CONFIG['min']
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay'])
        )
        async def get_ticket_details():
            err_msg = None

            request = {
                'request_id': uuid(),
                'body': {
                    'ticket_id': ticket_id
                },
            }

            try:
                self._logger.info(f'Getting details of ticket {ticket_id} from Bruin...')
                response = await self._event_bus.rpc_request(
                    "bruin.ticket.details.request",
                    request,
                    self._timeout,
                )
            except Exception as e:
                err_msg = f'An error occurred when requesting ticket details ' \
                          f'from Bruin API for ticket {ticket_id} -> {e}'
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
                else:
                    self._logger.info(f'Got details of ticket {ticket_id} from Bruin!')

            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            return response

        try:
            return await get_ticket_details()
        except Exception as e:
            self._logger.error(f"Error getting ticket details for {ticket_id} from Bruin: {e}")

    async def get_site(self, site_id):
        # TODO add for ticket creation
        pass

    async def mark_email_as_done(self):
        pass

    async def get_tickets_basic_info(self, client_id: str, ticket_statuses: List[str], site_id: str):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG['multiplier'],
                min=self._config.NATS_CONFIG['min']
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay'])
        )
        async def get_tickets_basic_info():
            err_msg = None
            request = {
                'request_id': uuid(),
                'body': {
                    'client_id': client_id,
                    'ticket_statuses': ticket_statuses,
                    'site_id': site_id,
                },
            }

            try:
                self._logger.info(
                    f'Getting all tickets with any status of {ticket_statuses},'
                    f'and belonging to client {client_id} from Bruin...'
                )
                response = await self._event_bus.rpc_request(
                    "bruin.ticket.basic.request",
                    request,
                    timeout=self._timeout
                )
            except Exception as e:
                err_msg = (
                    f'An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses} '
                    f'and belonging to client {client_id} -> {e}'
                )
                response = nats_error_response
            else:
                response_body = response['body']
                response_status = response['status']

                if response_status in range(200, 300):
                    self._logger.info(
                        f'Got all tickets with any status of {ticket_statuses}, with ticket topic '
                        f'and belonging to client {client_id} from Bruin!'
                    )

                else:
                    err_msg = (
                        f'Error while retrieving tickets with any status of {ticket_statuses} '
                        f'and belonging to client {client_id} in '
                        f'{self._config.ENVIRONMENT.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)

            return response

        try:
            return await get_tickets_basic_info()
        except Exception as e:
            self._logger.error(f"Error getting tickets with client_id {client_id} from Bruin: {e}")

    async def get_open_tickets_with_service_numbers(self, client_id: str, site_ids: List[str]) -> Dict[str, Any]:
        ticket_statuses = ['New', 'InProgress', 'Draft']

        open_tickets = []
        self._logger.info(f'Getting open tickets for site_ids: {site_ids}')
        for site_id in site_ids:
            tickets = await self.get_tickets_basic_info(client_id, ticket_statuses, site_id)
            if tickets['status'] not in range(200, 300):
                return {'status': tickets['status'], 'body': 'Error while retrieving open tickets'}
            open_tickets.extend(tickets['body'])

        self._logger.info(f'Open tickets {open_tickets}')
        if not open_tickets:
            return {'status': 404, 'body': 'No open tickets found'}

        processed_tickets = []
        for ticket in open_tickets:
            processed_ticket = self._decamelize_ticket(ticket)
            ticket_id = processed_ticket['ticket_id']
            details = await self.get_ticket_details(ticket_id)
            if details['status'] not in range(200, 300):
                err_msg = f'Error while retrieving details from ticket {ticket_id}'
                self._logger(err_msg)
                self._notifications_repository.send_slack_message(err_msg)
                continue
            service_numbers = self._get_details_service_numbers(details['body'])
            processed_ticket['service_numbers'] = service_numbers
            processed_tickets.append(processed_ticket)

        return {'status': 200, 'body': processed_tickets}

    def _decamelize_ticket(self, ticket: Dict[str, Any]):
        decamelized_ticket = humps.decamelize(ticket)
        decamelized_ticket['ticket_id'] = ticket['ticketID']
        decamelized_ticket['client_id'] = ticket['clientID']
        return decamelized_ticket

    def _get_details_service_numbers(self, ticket_details: Dict[str, Any]) -> List[str]:
        notes = ticket_details.get('ticketNotes')
        unique_service_numbers = set()
        for note in notes:
            note_service_numbers = note.get('serviceNumber', [])
            if note_service_numbers:
                unique_service_numbers.update(note_service_numbers)
        return list(unique_service_numbers)
