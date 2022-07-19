import os
from datetime import datetime

from application.repositories import nats_error_response
from pytz import timezone
from shortuuid import uuid


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def append_note_to_ticket(self, ticket_id: int, note: str, wtns: list = None):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "note": note,
            },
        }
        if wtns:
            request["body"]["service_numbers"] = wtns

        try:
            self._logger.info(f"Appending note to ticket {ticket_id}... Note contents: {note}")
            response = await self._event_bus.rpc_request("bruin.ticket.note.append.request", request, timeout=60)
        except Exception as e:
            err_msg = (
                f"An error occurred when appending a ticket note to ticket {ticket_id}. "
                f"Ticket note: {note}. Error: {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Note appended to ticket {ticket_id}!")
            else:
                err_msg = (
                    f"Error while appending note to ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Note was {note}. Error: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_service_number_by_circuit_id(self, circuit_id):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "circuit_id": circuit_id,
            },
        }

        try:
            self._logger.info(f"Getting the translation to service number for circuit_id {circuit_id}")
            response = await self._event_bus.rpc_request("bruin.get.circuit.id", request, timeout=60)
        except Exception as e:
            err_msg = f"Getting the translation to service number for circuit_id {circuit_id} Error: {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300) or response_status == 204:
                err_msg = (
                    f"Getting the translation to service number for circuit_id {circuit_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Error: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_outage_ticket(self, client_id: int, service_number: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }

        try:
            self._logger.info(
                f"Creating outage ticket for device {service_number} that belongs to client {client_id}..."
            )
            response = await self._event_bus.rpc_request("bruin.ticket.creation.outage.request", request, timeout=30)
            self._logger.info(f"Outage ticket for device {service_number} that belongs to client {client_id} created!")
        except Exception as e:
            err_msg = (
                f"An error occurred when creating outage ticket for device {service_number} belong to client"
                f"{client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            is_bruin_custom_status = response_status in (409, 471, 472, 473)
            if not (response_status in range(200, 300) or is_bruin_custom_status):
                err_msg = (
                    f"Error while creating outage ticket for device {service_number} that belongs to client "
                    f"{client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_serial_attribute_from_inventory(self, service_number, client_id):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "status": "A",
                "service_number": service_number,
            },
        }

        try:
            self._logger.info(
                f"Getting inventory attributes' serial number for service number {service_number} and client ID"
                f" {client_id}"
            )
            response = await self._event_bus.rpc_request("bruin.inventory.attributes.serial", request, timeout=60)
        except Exception as e:
            err_msg = (
                f"Error while getting inventory attributes' serial number for service number {service_number} and "
                f"client ID {client_id}: {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Got inventory attributes' serial number for service number {service_number} and client ID "
                    f"{client_id}"
                )
            else:
                err_msg = (
                    f"Error while getting inventory attributes' serial number for service number {service_number} and "
                    f"client ID {client_id} in {self._config.ENVIRONMENT_NAME.upper()} environment. Error: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def append_intermapper_note(self, ticket_id, parsed_email_dict, is_piab_device):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        previous_condition = (
            f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n"
            if parsed_email_dict["previous_condition"]
            else ""
        )
        ip_address = (
            f"Wireless IP Address: {parsed_email_dict['address']}"
            if is_piab_device
            else f"IP Address: {parsed_email_dict['address']}"
        )

        intermapper_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"InterMapper Triage",
                f"Message from InterMapper {parsed_email_dict['version']}",
                "",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"{previous_condition}",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}",
                "",
                f"{ip_address}",
                "",
                f"IM Device Label:     {parsed_email_dict['name']}",
                "",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}",
                "",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"TimeStamp: {current_datetime_tz_aware}",
            ]
        )
        return await self.append_note_to_ticket(ticket_id, intermapper_note)

    async def append_intermapper_up_note(self, ticket_id, wtn, parsed_email_dict, is_piab_device):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        previous_condition = (
            f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n"
            if parsed_email_dict["previous_condition"]
            else ""
        )
        ip_address = (
            f"Wireless IP Address: {parsed_email_dict['address']}"
            if is_piab_device
            else f"IP Address: {parsed_email_dict['address']}"
        )

        intermapper_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"Message from InterMapper {parsed_email_dict['version']}",
                "",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"{previous_condition}",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}",
                "",
                f"{ip_address}",
                "",
                f"IM Device Label:     {parsed_email_dict['name']}",
                "",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}",
                "",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"TimeStamp: {current_datetime_tz_aware}",
            ]
        )
        return await self.append_note_to_ticket(ticket_id, intermapper_note, wtns=[wtn])

    async def append_autoresolve_note(self, ticket_id, wtn):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        intermapper_note = os.linesep.join(
            [f"#*MetTel's IPA*#", f"Auto-resolving task for {wtn}", f"TimeStamp: {current_datetime_tz_aware}"]
        )
        return await self.append_note_to_ticket(ticket_id, intermapper_note, wtns=[wtn])

    async def append_dri_note(self, ticket_id, dri_body, parsed_email_dict):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        sim_insert = dri_body["InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert"].split(" ")
        sim_note = f"SIM1 Provider:      {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers']}\n"
        if "SIM1" in sim_insert:
            sim_note = f"SIM1 Status:         {sim_insert[sim_insert.index('SIM1') + 1]}\n" + sim_note
        if "SIM2" in sim_insert:
            sim_note = sim_note + f"\nSIM2 Status:         {sim_insert[sim_insert.index('SIM2') + 1]}\n"
        previous_condition = (
            f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n"
            if parsed_email_dict["previous_condition"]
            else ""
        )
        dri_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"InterMapper Triage",
                f"Message from InterMapper {parsed_email_dict['version']}",
                "",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"{previous_condition}",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}",
                "",
                f"Wireless IP Address: {parsed_email_dict['address']}",
                "",
                f"IM Device Label:     {parsed_email_dict['name']}",
                "",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}",
                "",
                f"{sim_note}",
                f"WAN Mac Address:     "
                f"{dri_body['InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress']}",
                "",
                f"SIM ICC ID:          {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid']}",
                f"Subscriber Number:   {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum']}",
                "",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"Timestamp: {current_datetime_tz_aware}",
            ]
        )

        return await self.append_note_to_ticket(ticket_id, dri_note)

    async def unpause_ticket_detail(self, ticket_id: int, *, detail_id: int = None, service_number: str = None):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
            },
        }

        if detail_id:
            request["body"]["detail_id"] = detail_id

        if service_number:
            request["body"]["service_number"] = service_number

        try:
            self._logger.info(f"Unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}...")
            response = await self._event_bus.rpc_request("bruin.ticket.unpause", request, timeout=30)
        except Exception as e:
            err_msg = (
                f"An error occurred when unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}. "
                f"Error: {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Detail {detail_id} (serial {service_number}) of ticket {ticket_id} was unpaused!")
            else:
                err_msg = (
                    f"Error while unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment. "
                    f"Error: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def resolve_ticket(self, ticket_id: int, detail_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        try:
            self._logger.info(f"Resolving ticket {ticket_id} (affected detail ID: {detail_id})...")
            response = await self._event_bus.rpc_request("bruin.ticket.status.resolve", request, timeout=15)
            self._logger.info(f"Ticket {ticket_id} resolved!")
        except Exception as e:
            err_msg = f"An error occurred when resolving ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while resolving ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_ticket_basic_info(self, client_id: int, service_number: str = None):
        err_msg = None
        ticket_statuses = ["New", "InProgress", "Draft"]

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "ticket_statuses": ticket_statuses,
                "service_number": service_number,
                "ticket_topic": "VOO",
            },
        }

        try:
            self._logger.info(
                f"Getting all tickets basic info with any status of {ticket_statuses}, with ticket topic "
                f"VOO, service number {service_number} and belonging to client {client_id} from Bruin..."
            )

            response = await self._event_bus.rpc_request("bruin.ticket.basic.request", request, timeout=90)
        except Exception as e:
            err_msg = (
                f"An error occurred when requesting tickets  basic info from Bruin API with any status"
                f" of {ticket_statuses}, with ticket topic VOO and belonging to client {client_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Got all tickets basic info with any status of {ticket_statuses}, with ticket topic "
                    f"VOO, service number {service_number} and belonging to client "
                    f"{client_id} from Bruin!"
                )
            else:
                err_msg = (
                    f"Error while retrieving tickets basic info with any status of {ticket_statuses}, "
                    f"with ticket topic VOO, service number {service_number} and belonging to client {client_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_tickets(self, client_id: int, ticket_id):
        err_msg = None
        ticket_statuses = ["New", "InProgress", "Draft"]

        request = {
            "request_id": uuid(),
            "body": {
                "client_id": client_id,
                "ticket_status": ticket_statuses,
                "ticket_topic": "VOO",
                "ticket_id": ticket_id,
            },
        }

        try:
            self._logger.info(f"Getting all tickets of ticket id {ticket_id} from Bruin...")

            response = await self._event_bus.rpc_request("bruin.ticket.request", request, timeout=90)
        except Exception as e:
            err_msg = f"An error occurred when requesting all tickets of ticket id {ticket_id} from Bruin API -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(f"Got all tickets of ticket id {ticket_id} from Bruin")
            else:
                err_msg = (
                    f"Error while retrieving all tickets of ticket id {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_ticket_details(self, ticket_id: int):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"ticket_id": ticket_id},
        }

        try:
            self._logger.info(f"Getting details of ticket {ticket_id} from Bruin...")
            response = await self._event_bus.rpc_request("bruin.ticket.details.request", request, timeout=15)
            self._logger.info(f"Got details of ticket {ticket_id} from Bruin!")
        except Exception as e:
            err_msg = f"An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving details of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def send_forward_email_milestone_notification(self, ticket_id: int, service_number: str) -> dict:
        notification_type = "TicketPIABDeviceLostPower-E-Mail"
        return await self.post_notification_email_milestone(ticket_id, service_number, notification_type)

    async def post_notification_email_milestone(self, ticket_id: int, service_number: str, notification_type: str):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "ticket_id": ticket_id,
                "service_number": service_number,
                "notification_type": notification_type,
            },
        }

        try:
            self._logger.info(
                f"Sending email for ticket id {ticket_id}, "
                f"service_number {service_number} "
                f"and notification type {notification_type}..."
            )
            response = await self._event_bus.rpc_request("bruin.notification.email.milestone", request, timeout=90)
        except Exception as e:
            err_msg = (
                f"An error occurred when sending email for ticket id {ticket_id}, "
                f"service_number {service_number} "
                f"and notification type {notification_type}...-> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Email sent for ticket {ticket_id}, service number {service_number} "
                    f"and notification type {notification_type}!"
                )
            else:
                err_msg = (
                    f"Error while sending email for ticket id {ticket_id}, service_number {service_number} "
                    f"and notification type {notification_type} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def change_detail_work_queue(
        self,
        ticket_id: int,
        task_result: str,
        serial_number: str,
    ):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"ticket_id": ticket_id, "queue_name": task_result, "service_number": serial_number},
        }

        try:
            self._logger.info(
                f"Changing task result for ticket {ticket_id} for device {serial_number} to {task_result}..."
            )
            response = await self._event_bus.rpc_request("bruin.ticket.change.work", request, timeout=90)
        except Exception as e:
            err_msg = f"An error occurred when changing task result for ticket {ticket_id} and serial {serial_number}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Ticket {ticket_id} and serial {serial_number} task result changed to {task_result} successfully!"
                )
            else:
                err_msg = (
                    f"Error while changing task result for ticket {ticket_id} and serial {serial_number} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
