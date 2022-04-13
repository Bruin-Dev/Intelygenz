import math
import os
from datetime import datetime
from typing import List

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
                'ticket_statuses': ticket_statuses,
                'ticket_topic': ticket_topic,
                'product_category': self._config.PRODUCT_CATEGORY,
            },
        }

        if client_id:
            request['body']['client_id'] = client_id
        if service_number:
            request['body']['service_number'] = service_number

        try:
            self._logger.info(f'Getting all tickets with parameters of {request["body"]} from Bruin...')

            response = await self._event_bus.rpc_request("bruin.ticket.basic.request", request, timeout=90)
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting tickets from Bruin API with parameters of {request["body"]} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Got all tickets with parameters of {request["body"]} from Bruin!'
                )
            else:
                err_msg = (
                    f'Error while retrieving tickets with parameters of {request["body"]} in '
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_ticket(self, ticket_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
            },
        }

        try:
            self._logger.info(f'Getting info of ticket {ticket_id}...')
            response = await self._event_bus.rpc_request("bruin.single_ticket.basic.request", request, timeout=15)
        except Exception as e:
            err_msg = f'An error occurred when requesting info of ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Got info of ticket {ticket_id} from Bruin!')
            else:
                err_msg = (
                    f'Error while retrieving info of ticket {ticket_id} in '
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
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
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
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
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment. Note was {note}. Error: '
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
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
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
                    f'client {client_id} in {self._config.CURRENT_ENVIRONMENT.upper()} environment: '
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
                    f'Error while resolving ticket {ticket_id} in {self._config.CURRENT_ENVIRONMENT.upper()} '
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
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
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
                    f'{client_id} in {self._config.CURRENT_ENVIRONMENT.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def change_detail_work_queue(self, ticket_id: int, task_result: str, *, serial_number: str = None,
                                       detail_id: int = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "ticket_id": ticket_id,
                "queue_name": task_result
            },
        }
        if serial_number:
            request['body']["service_number"] = serial_number
        if detail_id:
            request['body']["detail_id"] = detail_id
        try:
            self._logger.info(
                f'Changing task result for ticket {ticket_id} and detail id {detail_id} for device '
                f'{serial_number} to {task_result}...')
            response = await self._event_bus.rpc_request("bruin.ticket.change.work", request, timeout=90)
        except Exception as e:
            err_msg = (
                f'An error occurred when changing task result for ticket {ticket_id} and serial {serial_number}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Ticket {ticket_id} and serial {serial_number} task result changed to  {task_result}')
            else:
                err_msg = (
                    f'Error while changing task result for ticket {ticket_id} and serial {serial_number} in '
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_ticket_overview(self, ticket_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
            },
        }

        try:
            self._logger.info(f'Getting overview for ticket id {ticket_id} ...')
            response = await self._event_bus.rpc_request("bruin.ticket.overview.request", request, timeout=30)
        except Exception as e:
            err_msg = f'An error occurred when getting overview for ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Got overview of ticket {ticket_id}!')
            else:
                err_msg = (
                    f'Error while getting overview for ticket {ticket_id} in '
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
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
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment. '
                    f'Error: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def change_ticket_severity(self, ticket_id: int, severity_level: int, reason_for_change: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'severity': severity_level,
                'reason': reason_for_change,
            },
        }

        try:
            self._logger.info(f'Changing severity level of ticket {ticket_id} to {severity_level}...')
            response = await self._event_bus.rpc_request("bruin.change.ticket.severity", request, timeout=45)
        except Exception as e:
            err_msg = (
                f'An error occurred when changing the severity level of ticket {ticket_id} to {severity_level} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Severity level of ticket {ticket_id} successfully changed to {severity_level}!')
            else:
                err_msg = (
                    f'Error while changing severity of ticket {ticket_id} to {severity_level} in '
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
        else:
            success_msg = (
                f'Severity level of Service Outage ticket {ticket_id} changed to {severity_level}: '
                f'https://app.bruin.com/t/{ticket_id}'
            )
            await self._notifications_repository.send_slack_message(success_msg)

        return response

    async def post_notification_email_milestone(self, ticket_id: int, service_number: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'service_number': service_number,
                'notification_type': 'TicketBYOBOutageRepairAcknowledgement-E-Mail'

            },
        }

        try:
            self._logger.info(f'Sending email for ticket id {ticket_id} and service_number {service_number}...')
            response = await self._event_bus.rpc_request("bruin.notification.email.milestone", request, timeout=90)
        except Exception as e:
            err_msg = f'An error occurred when sending email for ticket id {ticket_id} and ' \
                      f'service_number {service_number} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Email sent for ticket {ticket_id} and service_number {service_number}!')
            else:
                err_msg = (
                    f'Error while sending email for ticket id {ticket_id} and service_number {service_number} in '
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_autoresolve_note_to_ticket(self, ticket_id: int, serial_number):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        autoresolve_note = os.linesep.join([
            "#*MetTel's IPA*#",
            f'Auto-resolving detail for serial: {serial_number}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, autoresolve_note, service_numbers=[serial_number])

    async def append_reopening_note_to_ticket(self, ticket_id: int, service_number: str, outage_causes: str):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        reopening_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'Re-opening ticket.',
            f'{outage_causes}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, reopening_note, service_numbers=[service_number])

    async def get_outage_tickets(self, client_id: int, ticket_statuses: list, *, service_number: str = None):
        ticket_topic = 'VOO'

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses, service_number=service_number)

    async def get_open_outage_tickets(self, *, client_id: int = None, service_number: str = None):
        ticket_statuses = ['New', 'InProgress', 'Draft']

        return await self.get_outage_tickets(client_id, ticket_statuses, service_number=service_number)

    @staticmethod
    def is_management_status_active(management_status: str):
        return management_status in {"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"}

    async def append_triage_note(self, ticket_detail, ticket_note):
        ticket_id = ticket_detail['ticket_id']
        ticket_detail_id = ticket_detail['ticket_detail']['detailID']
        service_number = ticket_detail['ticket_detail']['detailValue']

        if self._config.CURRENT_ENVIRONMENT == 'dev':
            triage_message = (
                f'Triage note would have been appended to detail {ticket_detail_id} of ticket {ticket_id}'
                f'(serial: {service_number}). Note: {ticket_note}. Details at app.bruin.com/t/{ticket_id}'
            )
            self._logger.info(triage_message)
            await self._notifications_repository.send_slack_message(triage_message)
            return None
        elif self._config.CURRENT_ENVIRONMENT == 'production':
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
                        accumulator = "#*MetTel's IPA*#\n" \
                                      "Triage (VeloCloud)\n"
            return 200

    async def append_digi_reboot_note(self, ticket_id, serial_number, interface):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))

        digi_reboot_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'Offline DiGi interface identified for serial: {serial_number}',
            f'Interface: {interface}',
            f'Automatic reboot attempt started.',
            f'TimeStamp: {current_datetime_tz_aware}'
        ])
        return await self.append_note_to_ticket(ticket_id, digi_reboot_note, service_numbers=[serial_number])

    async def append_task_result_change_note(self, ticket_id, task_result):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        task_result_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'DiGi reboot failed',
            f'Moving task to: {task_result}',
            f'TimeStamp: {current_datetime_tz_aware}'
        ])
        return await self.append_note_to_ticket(ticket_id, task_result_note)

    async def append_asr_forwarding_note(self, ticket_id, links, serial_number):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))

        note_lines = [
            f"#*MetTel's IPA*#",
        ]

        for link in links:
            note_lines.append(
                f'Status of Wired Link {link["interface"]} ({link["displayName"]}) is {link["linkState"]}.'
            )

        note_lines += [
            f'Moving task to: ASR Investigate',
            f'TimeStamp: {current_datetime_tz_aware}',
        ]

        task_result_note = os.linesep.join(note_lines)
        return await self.append_note_to_ticket(ticket_id, task_result_note, service_numbers=[serial_number])

    async def change_ticket_severity_for_offline_edge(self, ticket_id: int):
        severity_level = self._config.MONITOR_CONFIG['severity_by_outage_type']['edge_down']
        reason_for_change = os.linesep.join([
            "#*MetTel's IPA*#",
            f'Changing to Severity {severity_level}',
            'Edge Status: Offline',
        ])
        return await self.change_ticket_severity(ticket_id, severity_level, reason_for_change)

    async def change_ticket_severity_for_disconnected_links(self, ticket_id: int, links: List[str]):
        severity_level = self._config.MONITOR_CONFIG['severity_by_outage_type']['link_down']

        reason_for_change_lines = [
            "#*MetTel's IPA*#",
            f'Changing to Severity {severity_level}',
            'Edge Status: Online',
        ]
        reason_for_change_lines += [
            f'Interface {link} Status: Disconnected'
            for link in links
        ]

        reason_for_change = os.linesep.join(reason_for_change_lines)
        return await self.change_ticket_severity(ticket_id, severity_level, reason_for_change)
