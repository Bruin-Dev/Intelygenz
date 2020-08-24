import os

from datetime import datetime, timedelta

from pytz import timezone
from shortuuid import uuid

from application.repositories import nats_error_response


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_closed_tickets(self, client_id, ticket_topic):
        err_msg = None

        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        self._logger.info(
            f'Getting tickets that belongs to client: {client_id}')
        request_msg = {
            "request_id": uuid(),
            "body": {"client_id": client_id,
                     "category": "SD-WAN",
                     "ticket_topic": ticket_topic,
                     "ticket_status": ['Closed'],
                     "start_date": start_date,
                     "end_date": end_date,
                     }
        }
        try:
            response = await self._event_bus.rpc_request("bruin.ticket.request", request_msg, timeout=60)
            self._logger.info(
                f'Got all closed tickets with, with ticket topic '
                f'{ticket_topic} and belonging to client {client_id} from Bruin!'
            )
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting closed tickets from Bruin API, '
                f'with ticket topic {ticket_topic} and belonging to client {client_id} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving closed tickets, with ticket topic '
                    f'{ticket_topic} and belonging to client {client_id} in '
                    f'{self._config.TNBA_FEEDBACK_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_outage_tickets(self, client_id: int):
        ticket_topic = 'VOO'

        return await self.get_closed_tickets(client_id, ticket_topic)

    async def get_affecting_tickets(self, client_id: int):
        ticket_topic = 'VAS'

        return await self.get_closed_tickets(client_id, ticket_topic)

    async def get_ticket_task_history(self, ticket_id):
        err_msg = None

        self._logger.info(
            f'Getting ticket task history for app.bruin.com/t/{ticket_id}')
        request_msg = {
            "request_id": uuid(),
            "body": {
                        "ticket_id": ticket_id
                    }
        }
        try:
            response = await self._event_bus.rpc_request("bruin.ticket.get.task.history", request_msg, timeout=60)
            self._logger.info(f'Got task_history of ticket {ticket_id} from Bruin!')

        except Exception as e:

            err_msg = f'An error occurred when requesting ticket task_history from Bruin API for ticket {ticket_id} ' \
                      f'-> {e}'

            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving task history of ticket {ticket_id} in '
                    f'{self._config.TNBA_FEEDBACK_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
