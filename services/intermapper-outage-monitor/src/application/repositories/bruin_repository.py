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

    async def append_note_to_ticket(self, ticket_id: int, note: str, wtns: list = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': note,
            },
        }
        if wtns:
            request['body']['service_numbers'] = wtns

        try:
            self._logger.info(f'Appending note to ticket {ticket_id}... Note contents: {note}')
            response = await self._event_bus.rpc_request("bruin.ticket.note.append.request", request, timeout=60)
        except Exception as e:
            err_msg = (
                f'An error occurred when appending a ticket note to ticket {ticket_id}. '
                f'Ticket note: {note}. Error: {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Note appended to ticket {ticket_id}!')
            else:
                err_msg = (
                    f'Error while appending note to ticket {ticket_id} in '
                    f'{self._config.INTERMAPPER_CONFIG["environment"].upper()} environment. Note was {note}. Error: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_circuit_id(self, circuit_id):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'circuit_id': circuit_id,
            },
        }

        try:
            self._logger.info(f'Getting the translation of circuit_id {circuit_id}')
            response = await self._event_bus.rpc_request("bruin.get.circuit.id", request, timeout=60)
        except Exception as e:
            err_msg = (
                f'Getting the translation of circuit_id {circuit_id} Error: {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300) or response_status == 204:
                err_msg = (
                    f'Getting the translation of circuit_id {circuit_id} in '
                    f'{self._config.INTERMAPPER_CONFIG["environment"].upper()} environment. Error: '
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

            is_bruin_custom_status = response_status in (409, 471, 472, 473)
            if not (response_status in range(200, 300) or is_bruin_custom_status):
                err_msg = (
                    f'Error while creating outage ticket for device {service_number} that belongs to client '
                    f'{client_id} in {self._config.INTERMAPPER_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_attributes_serial(self, service_number, client_id):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "client_id": client_id,
                "status": "A",
                "service_number": service_number,
            },
        }

        try:
            self._logger.info(f"Getting the attribute's serial number of serial number {service_number}")
            response = await self._event_bus.rpc_request("bruin.inventory.attributes.serial", request, timeout=60)
        except Exception as e:
            err_msg = (
                f"Getting the attribute's serial number of serial number {service_number} Error: {e}"
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f"Got the attribute's serial number of serial number {service_number}!")
            else:
                err_msg = (
                    f"'Getting the attribute's serial number of serial number {service_number}'"
                    f'{self._config.INTERMAPPER_CONFIG["environment"].upper()} environment. Error: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_intermapper_note(self, ticket_id, parsed_email_dict):
        current_datetime_tz_aware = datetime.now(timezone(self._config.INTERMAPPER_CONFIG['timezone']))
        intermapper_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'InterMapper Triage',
            f"CONDITION: {parsed_email_dict['condition']}\n",
            f"Event:               {parsed_email_dict['event']}",
            f"Time of Event:       {parsed_email_dict['time']}\n",
            f"Wireless IP Address: {parsed_email_dict['address']}\n",
            f"IM Device Label:     {parsed_email_dict['name']}\n",
            f"IM Map Name: 	       {parsed_email_dict['document']}",
            f"Probe Type:          {parsed_email_dict['probe_type']}\n",
            f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
            f"Device's up time: {parsed_email_dict['up_time']}",
            f'TimeStamp: {current_datetime_tz_aware}'
        ])
        return await self.append_note_to_ticket(ticket_id, intermapper_note)

    async def append_intermapper_up_note(self, ticket_id, wtn, parsed_email_dict):
        current_datetime_tz_aware = datetime.now(timezone(self._config.INTERMAPPER_CONFIG['timezone']))
        intermapper_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f"CONDITION: {parsed_email_dict['condition']}\n",
            f"Event:               {parsed_email_dict['event']}",
            f"Time of Event:       {parsed_email_dict['time']}\n",
            f"Wireless IP Address: {parsed_email_dict['address']}\n",
            f"IM Device Label:     {parsed_email_dict['name']}\n",
            f"IM Map Name: 	       {parsed_email_dict['document']}",
            f"Probe Type:          {parsed_email_dict['probe_type']}\n",
            f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
            f"Device's up time: {parsed_email_dict['up_time']}",
            f'TimeStamp: {current_datetime_tz_aware}'
        ])
        return await self.append_note_to_ticket(ticket_id, intermapper_note, wtns=[wtn])

    async def append_autoresolve_note(self, ticket_id, wtn):
        current_datetime_tz_aware = datetime.now(timezone(self._config.INTERMAPPER_CONFIG['timezone']))
        intermapper_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'Auto-resolving task for {wtn}',
            f'TimeStamp: {current_datetime_tz_aware}'
        ])
        return await self.append_note_to_ticket(ticket_id, intermapper_note, wtns=[wtn])

    async def append_dri_note(self, ticket_id, dri_body, parsed_email_dict):
        current_datetime_tz_aware = datetime.now(timezone(self._config.INTERMAPPER_CONFIG['timezone']))
        sim_insert = dri_body["InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert"].split(' ')
        sim_note = f"SIM1 Provider:      {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers']}\n"
        if 'SIM1' in sim_insert:
            sim_note = f"SIM1 Status:         {sim_insert[sim_insert.index('SIM1') + 1]}\n" + sim_note
        if 'SIM2' in sim_insert:
            sim_note = sim_note + f"\nSIM2 Status:         {sim_insert[sim_insert.index('SIM2') + 1]}\n"

        dri_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f"InterMapper Triage",
            f"Message from InterMapper 6.1.5\n",
            f"CONDITION: {parsed_email_dict['condition']}\n",
            f"Event:               {parsed_email_dict['event']}",
            f"Time of Event:       {parsed_email_dict['time']}\n",
            f"Wireless IP Address: {parsed_email_dict['address']}\n",
            f"IM Device Label:     {parsed_email_dict['name']}\n",
            f"IM Map Name: 	       {parsed_email_dict['document']}",
            f"Probe Type:          {parsed_email_dict['probe_type']}\n",
            f"{sim_note}",
            f"WAN Mac Address:     "
            f"{dri_body['InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress']}\n",
            f"SIM ICC ID:          {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid']}",
            f"Subscriber Number:   {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum']}\n",
            f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
            f"Device's up time: {parsed_email_dict['up_time']}",
            f"Timestamp: {current_datetime_tz_aware}"])

        return await self.append_note_to_ticket(ticket_id, dri_note)

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
                    f'Error while resolving ticket {ticket_id} in '
                    f'{self._config.INTERMAPPER_CONFIG["environment"].upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_ticket_basic_info(self, client_id: int, service_number: str = None):
        err_msg = None
        ticket_statuses = ['New', 'InProgress', 'Draft']

        request = {
            'request_id': uuid(),
            'body': {
                'client_id': client_id,
                'ticket_statuses': ticket_statuses,
                'service_number': service_number,
                'ticket_topic': 'VOO',
            },
        }

        try:
            self._logger.info(
                f'Getting all tickets basic info with any status of {ticket_statuses}, with ticket topic '
                f'VOO, service number {service_number} and belonging to client {client_id} from Bruin...'
            )

            response = await self._event_bus.rpc_request("bruin.ticket.basic.request", request, timeout=90)
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting tickets  basic info from Bruin API with any status'
                f' of {ticket_statuses}, with ticket topic VOO and belonging to client {client_id} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Got all tickets basic info with any status of {ticket_statuses}, with ticket topic '
                    f'VOO, service number {service_number} and belonging to client '
                    f'{client_id} from Bruin!'
                )
            else:
                err_msg = (
                    f'Error while retrieving tickets basic info with any status of {ticket_statuses}, '
                    f'with ticket topic VOO, service number {service_number} and belonging to client {client_id} in '
                    f'{self._config.INTERMAPPER_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_tickets(self, client_id: int, ticket_id):
        err_msg = None
        ticket_statuses = ['New', 'InProgress', 'Draft']

        request = {
            'request_id': uuid(),
            'body': {
                'client_id': client_id,
                'ticket_status': ticket_statuses,
                'ticket_topic': 'VOO',
                'ticket_id': ticket_id
            },
        }

        try:
            self._logger.info(
                f'Getting all tickets of ticket id {ticket_id} from Bruin...'
            )

            response = await self._event_bus.rpc_request("bruin.ticket.request", request, timeout=90)
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting all tickets of ticket id {ticket_id} from Bruin API -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Got all tickets of ticket id {ticket_id} from Bruin'
                )
            else:
                err_msg = (
                    f'Error while retrieving all tickets of ticket id {ticket_id} in '
                    f'{self._config.INTERMAPPER_CONFIG["environment"].upper()} environment: '
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
                    f'{self._config.INTERMAPPER_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
