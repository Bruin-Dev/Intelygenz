from shortuuid import uuid

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
                else:
                    response['body'] = {
                        'client_id': client_id,
                        'site_id': response['body'].get('site_id'),
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
                response = await self._event_bus.rpc_request("bruin.ticket.details.request", request, timeout=15)
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
                        f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
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

    async def get_tickets_basic_info(self, client_id: str, ticket_statuses: List[str]):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG['multiplier'],
                min=self._config.NATS_CONFIG['min']
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay'])
        )
        async def get_tickets():
            err_msg = None
            request = {
                'request_id': uuid(),
                'body': {
                    # TODO add site id
                    'client_id': client_id,
                    'ticket_statuses': ticket_statuses
                },
            }

            try:
                self._logger.info(
                    f'Getting all tickets with any status of {ticket_statuses},'
                    f'and belonging to client {client_id} from Bruin...'
                )
                response = await self._event_bus.rpc_request("bruin.ticket.basic.request", request, timeout=90)
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
                        f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
            if err_msg:
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)

            return response

        try:
            return await get_tickets()
        except Exception as e:
            self._logger.error(f"Error getting tickets with client_id {client_id} from Bruin: {e}")

    async def get_open_tickets_with_serial_numbers(self, client_id: str) -> Dict[str, Any]:
        ticket_statuses = ['New', 'InProgress', 'Draft']

        tickets = await self.get_tickets_basic_info(client_id, ticket_statuses)
        for idx, ticket in enumerate(tickets):
            ticket_id = ticket['ticketId']
            details = await self.get_ticket_details(ticket_id)
            serial_numbers = self._get_details_serial_numbers(details)
            ticket[idx]['serial_numbers'] = serial_numbers

        return tickets

    def _get_details_serial_numbers(self, ticket_details: Dict[str, Any]) -> List[str]:
        notes = ticket_details.get('ticketNotes')
        unique_serial_numbers = set()
        for note in notes:
            note_serial_numbers = note.get('serviceNumber', [])
            unique_serial_numbers.add(*note_serial_numbers)
        return list(unique_serial_numbers)
