import os
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories.bruin_repository import BruinRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


class TestBruinRepository:
    def instance_test(self, bruin_repository, event_bus, logger, notifications_repository):
        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._logger is logger
        assert bruin_repository._config is testconfig
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def append_note_to_ticket_test(self):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Note appended with success",
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def append_note_to_ticket_wtn_provided_test(self):
        circuit_id = 1234
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id, "note": ticket_note, "service_numbers": [circuit_id]},
        }
        response = {
            "request_id": uuid_,
            "body": "Note appended with success",
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note, wtns=[circuit_id])

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_rpc_request_failing_test(self):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_2xx_status_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_409_status_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 409,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_471_status_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 471,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_472_status_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 472,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_473_status_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 473,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_rpc_request_failing_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_rpc_request_returning_no_2xx_or_409_or_471_status_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_service_number_by_circuit_id_test(self):
        circuit_id = "123"
        client_id = 83959

        request = {
            "request_id": uuid_,
            "body": {
                "circuit_id": circuit_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": {"clientID": 83959, "subAccount": "string", "wtn": "3214", "inventoryID": 0, "addressID": 0},
            "status": 200,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_service_number_by_circuit_id(circuit_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.get.circuit.id", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_service_number_by_circuit_id_failing_rpc_request_test(self):
        circuit_id = "123"

        request = {
            "request_id": uuid_,
            "body": {
                "circuit_id": circuit_id,
            },
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_service_number_by_circuit_id(circuit_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.get.circuit.id", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_service_number_by_circuit_id_non_2xx_response_test(self):
        circuit_id = "123"
        client_id = 83959

        request = {
            "request_id": uuid_,
            "body": {
                "circuit_id": circuit_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_service_number_by_circuit_id(circuit_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.get.circuit.id", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_serial_attribute_from_inventory_test(self):
        circuit_id = "123"
        client_id = 83959

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "status": "A",
                "service_number": circuit_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "705286",
            "status": 200,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_serial_attribute_from_inventory(circuit_id, client_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.attributes.serial", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_serial_attribute_from_inventory_rpc_request_test(self):
        circuit_id = "123"
        client_id = 83959

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "status": "A",
                "service_number": circuit_id,
            },
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_serial_attribute_from_inventory(circuit_id, client_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.attributes.serial", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_service_number_by_circuit_id_non_2xx_response_test(self):
        circuit_id = "123"
        client_id = 83959

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "status": "A",
                "service_number": circuit_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_serial_attribute_from_inventory(circuit_id, client_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.attributes.serial", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def append_intermapper_note_test(self):
        ticket_id = 11111
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "version": "6.1.5",
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "OK",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        intermapper_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"InterMapper Triage",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}\n",
                f"IP Address: {parsed_email_dict['address']}\n",
                f"IM Device Label:     {parsed_email_dict['name']}\n",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"TimeStamp: {current_datetime}",
            ]
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_intermapper_note(ticket_id, parsed_email_dict, False)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, intermapper_note)

    @pytest.mark.asyncio
    async def append_intermapper_note_no_previous_condition_test(self):
        ticket_id = 11111
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "event": "Alarm",
            "version": "6.1.5",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        intermapper_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"InterMapper Triage",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                "",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}\n",
                f"IP Address: {parsed_email_dict['address']}\n",
                f"IM Device Label:     {parsed_email_dict['name']}\n",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"TimeStamp: {current_datetime}",
            ]
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_intermapper_note(ticket_id, parsed_email_dict, False)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, intermapper_note)

    @pytest.mark.asyncio
    async def append_intermapper_note_piab_device_test(self):
        ticket_id = 11111
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "version": "6.1.5",
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "OK",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        intermapper_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"InterMapper Triage",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}\n",
                f"Wireless IP Address: {parsed_email_dict['address']}\n",
                f"IM Device Label:     {parsed_email_dict['name']}\n",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"TimeStamp: {current_datetime}",
            ]
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_intermapper_note(ticket_id, parsed_email_dict, True)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, intermapper_note)

    @pytest.mark.asyncio
    async def append_intermapper_up_note_test(self):
        ticket_id = 11111
        circuit_id = 1345
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "event": "Alarm",
            "version": "6.1.5",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "OK",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        intermapper_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}\n",
                f"IP Address: {parsed_email_dict['address']}\n",
                f"IM Device Label:     {parsed_email_dict['name']}\n",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"TimeStamp: {current_datetime}",
            ]
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_intermapper_up_note(ticket_id, circuit_id, parsed_email_dict, False)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, intermapper_note, wtns=[circuit_id])

    @pytest.mark.asyncio
    async def append_intermapper_up_note_no_previous_condition_test(self):
        ticket_id = 11111
        circuit_id = 1345
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "version": "6.1.5",
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        intermapper_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                "",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}\n",
                f"IP Address: {parsed_email_dict['address']}\n",
                f"IM Device Label:     {parsed_email_dict['name']}\n",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"TimeStamp: {current_datetime}",
            ]
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_intermapper_up_note(ticket_id, circuit_id, parsed_email_dict, False)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, intermapper_note, wtns=[circuit_id])

    @pytest.mark.asyncio
    async def append_intermapper_up_note_piab_device_test(self):
        ticket_id = 11111
        circuit_id = 1345
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "event": "Alarm",
            "version": "6.1.5",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "SNMP - Adtran TA900 ( SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "OK",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        intermapper_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}\n",
                f"Wireless IP Address: {parsed_email_dict['address']}\n",
                f"IM Device Label:     {parsed_email_dict['name']}\n",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"TimeStamp: {current_datetime}",
            ]
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_intermapper_up_note(ticket_id, circuit_id, parsed_email_dict, True)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, intermapper_note, wtns=[circuit_id])

    @pytest.mark.asyncio
    async def append_autoresolve_note_test(self):
        ticket_id = 11111
        circuit_id = 1345

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        current_datetime = datetime.now()
        intermapper_note = os.linesep.join(
            [f"#*MetTel's IPA*#", f"Auto-resolving task for {circuit_id}", f"TimeStamp: {current_datetime}"]
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_autoresolve_note(ticket_id, circuit_id)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, intermapper_note, wtns=[circuit_id])

    @pytest.mark.asyncio
    async def append_dri_note_test(self):
        ticket_id = 11111
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "version": "6.1.5",
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "Data Remote Probe (port 161 SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "OK",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        dri_body = {
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "SIM1 Active and SIM2 Ready",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
            "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "8C:19:2D:69",
        }

        sim_insert = dri_body["InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert"].split(" ")

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        sim_note = os.linesep.join(
            [
                f"SIM1 Status:         {sim_insert[sim_insert.index('SIM1') + 1]}",
                f"SIM1 Provider:      {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers']}",
                f"\nSIM2 Status:         {sim_insert[sim_insert.index('SIM2') + 1]}\n",
            ]
        )

        current_datetime = datetime.now()
        dri_body_add = dri_body["InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress"]
        sub_number = dri_body["InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum"]
        dri_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"InterMapper Triage",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n",
                f"Event:               {parsed_email_dict['event']}",
                f"Time of Event:       {parsed_email_dict['time']}\n",
                f"Wireless IP Address: {parsed_email_dict['address']}\n",
                f"IM Device Label:     {parsed_email_dict['name']}\n",
                f"IM Map Name: 	       {parsed_email_dict['document']}",
                f"Probe Type:          {parsed_email_dict['probe_type']}\n",
                f"{sim_note}",
                f"WAN Mac Address:     " f"{dri_body_add}\n",
                f"SIM ICC ID:          {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid']}",
                f"Subscriber Number:   {sub_number}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"Timestamp: {current_datetime}",
            ]
        )

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_dri_note(ticket_id, dri_body, parsed_email_dict)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, dri_note)

    @pytest.mark.asyncio
    async def append_dri_note_no_previous_condition_test(self):
        ticket_id = 11111
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "version": "6.1.5",
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "Data Remote Probe (port 161 SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        dri_body = {
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "SIM1 Active and SIM2 Ready",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
            "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "8C:19:2D:69",
        }

        sim_insert = dri_body["InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert"].split(" ")

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        sim_note = os.linesep.join(
            [
                f"SIM1 Status:         {sim_insert[sim_insert.index('SIM1') + 1]}",
                f"SIM1 Provider:      {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers']}",
                f"\nSIM2 Status:         {sim_insert[sim_insert.index('SIM2') + 1]}\n",
            ]
        )

        current_datetime = datetime.now()
        sub_number = dri_body["InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum"]
        dri_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"InterMapper Triage",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                "",
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
                f"Subscriber Number:   {sub_number}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"Timestamp: {current_datetime}",
            ]
        )

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_dri_note(ticket_id, dri_body, parsed_email_dict)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, dri_note)

    @pytest.mark.asyncio
    async def append_dri_note_no_sims_test(self):
        ticket_id = 11111
        parsed_email_dict = {
            "time": "01/10 15:35:40",
            "version": "6.1.5",
            "event": "Alarm",
            "name": "OReilly-HotSpringsAR(SD-WAN)-Site803",
            "document": "O Reilly Auto Parts - South East |83959| Platinum Monitoring",
            "address": "1.3.4",
            "probe_type": "Data Remote Probe (port 161 SNMPv2c)",
            "condition": '\t\tdefined("lcpu.avgBusy1") && (lcpu.avgBusy1 > 90)',
            "previous_condition": "OK",
            "last_reported_down": "7 days, 23 hours, 54 minutes, 10 seconds",
            "up_time": "209 days, 10 hours, 44 minutes, 16 seconds",
        }

        dri_body = {
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "",
            "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
            "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": "8C:19:2D:69",
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        sim_note = os.linesep.join(
            [
                f"SIM1 Provider:      {dri_body['InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers']}\n",
            ]
        )

        current_datetime = datetime.now()
        sub_number = dri_body["InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum"]
        dri_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"InterMapper Triage",
                f"Message from InterMapper {parsed_email_dict['version']}\n",
                f"CONDITION: {parsed_email_dict['condition']}",
                f"PREVIOUS CONDITION: {parsed_email_dict['previous_condition']}\n",
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
                f"Subscriber Number:   {sub_number}\n",
                f"Time since last reported down: {parsed_email_dict['last_reported_down']}",
                f"Device's up time: {parsed_email_dict['up_time']}",
                f"Timestamp: {current_datetime}",
            ]
        )

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            await bruin_repository.append_dri_note(ticket_id, dri_body, parsed_email_dict)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, dri_note)

    @pytest.mark.asyncio
    async def get_ticket_basic_info_with_service_number_specified_test(self):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": [
                {"ticketID": 11111},
                {"ticketID": 22222},
            ],
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_basic_info(bruin_client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.basic.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_basic_info_with_rpc_request_failing_test(self):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
                "service_number": service_number,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_basic_info(bruin_client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.basic.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_basic_info_with_rpc_request_returning_non_2xx_status_test(self):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_basic_info(bruin_client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.basic.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_test(self):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"
        ticket_id = 54321

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_status": ticket_statuses,
                "ticket_topic": ticket_topic,
                "ticket_id": ticket_id,
            },
        }

        response = {
            "request_id": uuid_,
            "body": [
                {"ticketID": 11111, "category": "DSL"},
            ],
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_rpc_request_failing_test(self):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"
        ticket_id = 54321

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_status": ticket_statuses,
                "ticket_topic": ticket_topic,
                "ticket_id": ticket_id,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets_rpc_request_returning_non_2xx_status_test(self):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"
        ticket_id = 54321

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_status": ticket_statuses,
                "ticket_topic": ticket_topic,
                "ticket_id": ticket_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": {
                "ticketDetails": [
                    {
                        "detailID": 2746938,
                        "detailValue": "VC1234567890",
                    },
                ],
                "ticketNotes": [
                    {
                        "noteId": 41894043,
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    },
                    {
                        "noteId": 41894044,
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    },
                ],
            },
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.details.request", request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_failing_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.details.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.details.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.resolve", request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_with_rpc_request_failing_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.resolve", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def resolve_ticket_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.resolve", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_only_detail_id_specified_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_only_service_number_specified_test(self):
        ticket_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number=service_number)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_detail_id_and_service_number_specified_test(self):
        ticket_id = 12345
        detail_id = 67890
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(
                ticket_id, detail_id=detail_id, service_number=service_number
            )

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_rpc_request_failing_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def send_forward_email_milestone_notification_test(self, bruin_repository, bruin_generic_200_response):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketPIABDeviceLostPower-E-Mail"
        bruin_repository._event_bus.rpc_request.return_value = bruin_generic_200_response

        response = await bruin_repository.send_forward_email_milestone_notification(ticket_id, service_number)

        bruin_repository.post_notification_email_milestone.assert_awaited_once_with(
            ticket_id, service_number, notification_type
        )
        assert response == bruin_generic_200_response
        bruin_repository._logger.error.assert_not_called()

    @pytest.mark.asyncio
    async def post_notification_email_milestone_test(self, bruin_repository, bruin_generic_200_response):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketPIABDeviceLostPower-E-Mail"
        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id, "service_number": service_number, "notification_type": notification_type},
        }
        bruin_repository._event_bus.rpc_request.return_value = bruin_generic_200_response

        with uuid_mock:
            result = await bruin_repository.post_notification_email_milestone(
                ticket_id, service_number, notification_type
            )

            bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
                "bruin.notification.email.milestone", request, timeout=90
            )
            bruin_repository._notifications_repository.send_slack_message.assert_not_awaited()
            bruin_repository._logger.error.assert_not_called()
            bruin_repository._notifications_repository.send_slack_message.assert_not_awaited()
            assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def post_notification_email_milestone_with_rpc_request_failing_test(
        self, bruin_repository, make_post_notification_email_milestone_request
    ):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketPIABDeviceLostPower-E-Mail"
        request = make_post_notification_email_milestone_request(
            request_id=uuid_, ticket_id=ticket_id, service_number=service_number, notification_type=notification_type
        )
        bruin_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        slack_message = (
            f"An error occurred when sending email for ticket id {ticket_id}, "
            f"service_number {service_number} and notification type {notification_type}...-> "
        )

        with uuid_mock:
            result = await bruin_repository.post_notification_email_milestone(
                ticket_id, service_number, notification_type
            )

            bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
                "bruin.notification.email.milestone", request, timeout=90
            )
            bruin_repository._notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
            bruin_repository._logger.error.assert_called_once_with(
                "An error occurred when sending email for ticket id 12345, service_number VC1234567 "
                f"and notification type {notification_type}...-> "
            )
            assert result == nats_error_response

    @pytest.mark.asyncio
    async def post_notification_email_milestone_with_rpc_request_returning__non_2xx_status_test(
        self, bruin_repository, bruin_500_response, make_post_notification_email_milestone_request
    ):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketPIABDeviceLostPower-E-Mail"
        request = make_post_notification_email_milestone_request(
            request_id=uuid_, ticket_id=ticket_id, service_number=service_number, notification_type=notification_type
        )
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        bruin_repository._event_bus.rpc_request.return_value = bruin_500_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        slack_message = (
            f"Error while sending email for ticket id {ticket_id}, service_number {service_number} "
            f"and notification type {notification_type} in "
            f"{testconfig.CURRENT_ENVIRONMENT.upper()} environment: "
            f'Error {bruin_500_response["status"]} - {bruin_500_response["body"]}'
        )

        with uuid_mock:
            result = await bruin_repository.post_notification_email_milestone(
                ticket_id, service_number, notification_type
            )

            bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
                "bruin.notification.email.milestone", request, timeout=90
            )
            bruin_repository._notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
            bruin_repository._logger.error.assert_called_once_with(
                "Error while sending email for ticket id 12345, service_number VC1234567 "
                f"and notification type {notification_type} "
                "in DEV environment: Error 500 - Got internal error from Bruin"
            )
            assert result == bruin_500_response
