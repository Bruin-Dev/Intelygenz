import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories.bruin_repository import BruinRepository
from application.repositories.utils_repository import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


class TestBruinRepository:
    def instance_test(self, bruin_repository, nats_client, notifications_repository):
        assert bruin_repository._nats_client is nats_client
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Note appended with success",
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        nats_client.request.assert_awaited_once_with("bruin.ticket.note.append.request", encoded_request, timeout=60)
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Note appended with success",
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note, wtns=[circuit_id])

        nats_client.request.assert_awaited_once_with("bruin.ticket.note.append.request", encoded_request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_request_failing_test(self):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
            },
        }
        encoded_request = to_json_bytes(request)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        nats_client.request.assert_awaited_once_with("bruin.ticket.note.append.request", encoded_request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_request_returning_non_2xx_status_test(self):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
            },
        }
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        nats_client.request.assert_awaited_once_with("bruin.ticket.note.append.request", encoded_request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", encoded_request, timeout=30
        )
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 409,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", encoded_request, timeout=30
        )
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 471,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", encoded_request, timeout=30
        )
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 472,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", encoded_request, timeout=30
        )
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 473,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", encoded_request, timeout=30
        )
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_request_failing_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        encoded_request = to_json_bytes(request)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", encoded_request, timeout=30
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_request_returning_no_2xx_or_409_or_471_status_test(self):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", encoded_request, timeout=30
        )
        notifications_repository.send_slack_message.assert_awaited_once()
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": {"clientID": 83959, "subAccount": "string", "wtn": "3214", "inventoryID": 0, "addressID": 0},
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_service_number_by_circuit_id(circuit_id)

        nats_client.request.assert_awaited_once_with("bruin.get.circuit.id", encoded_request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_service_number_by_circuit_id_failing_request_test(self):
        circuit_id = "123"

        request = {
            "request_id": uuid_,
            "body": {
                "circuit_id": circuit_id,
            },
        }
        encoded_request = to_json_bytes(request)

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_service_number_by_circuit_id(circuit_id)

        nats_client.request.assert_awaited_once_with("bruin.get.circuit.id", encoded_request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_service_number_by_circuit_id(circuit_id)

        nats_client.request.assert_awaited_once_with("bruin.get.circuit.id", encoded_request, timeout=60)
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "705286",
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_serial_attribute_from_inventory(circuit_id, client_id)

        nats_client.request.assert_awaited_once_with("bruin.inventory.attributes.serial", encoded_request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_serial_attribute_from_inventory_request_test(self):
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
        encoded_request = to_json_bytes(request)

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_serial_attribute_from_inventory(circuit_id, client_id)

        nats_client.request.assert_awaited_once_with("bruin.inventory.attributes.serial", encoded_request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_serial_attribute_from_inventory(circuit_id, client_id)

        nats_client.request.assert_awaited_once_with("bruin.inventory.attributes.serial", encoded_request, timeout=60)
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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.append_note_to_ticket = AsyncMock()

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
                "service_number": service_number,
                "ticket_topic": ticket_topic,
            },
        }
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": [
                {"ticketID": 11111},
                {"ticketID": 22222},
            ],
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_basic_info(bruin_client_id, service_number)

        nats_client.request.assert_awaited_once_with("bruin.ticket.basic.request", encoded_request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_basic_info_with_request_failing_test(self):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "service_number": service_number,
                "ticket_topic": ticket_topic,
            },
        }
        encoded_request = to_json_bytes(request)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_basic_info(bruin_client_id, service_number)

        nats_client.request.assert_awaited_once_with("bruin.ticket.basic.request", encoded_request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_basic_info_with_request_returning_non_2xx_status_test(self):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "service_number": service_number,
                "ticket_topic": ticket_topic,
            },
        }
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_basic_info(bruin_client_id, service_number)

        nats_client.request.assert_awaited_once_with("bruin.ticket.basic.request", encoded_request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": [
                {"ticketID": 11111, "category": "DSL"},
            ],
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.request", encoded_request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_request_failing_test(self):
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
        encoded_request = to_json_bytes(request)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.request", encoded_request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets_request_returning_non_2xx_status_test(self):
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.request", encoded_request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
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
        encoded_request = to_json_bytes(request)

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

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.details.request", encoded_request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details_with_request_failing_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }
        encoded_request = to_json_bytes(request)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.details.request", encoded_request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_details_with_request_returning_non_2xx_status_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.details.request", encoded_request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.status.resolve", encoded_request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_with_request_failing_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        encoded_request = to_json_bytes(request)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.status.resolve", encoded_request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def resolve_ticket_with_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        nats_client.request.assert_awaited_once_with("bruin.ticket.status.resolve", encoded_request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", encoded_request, timeout=30
        )
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number=service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", encoded_request, timeout=30
        )
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
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig
        notifications_repository = Mock()

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(
                ticket_id, detail_id=detail_id, service_number=service_number
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", encoded_request, timeout=30
        )
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_request_failing_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        encoded_request = to_json_bytes(request)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", encoded_request, timeout=30
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        encoded_request = to_json_bytes(request)

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", encoded_request, timeout=30
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def send_forward_email_milestone_notification_test(self, bruin_repository, bruin_generic_200_response):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketPIABDeviceLostPower-E-Mail"

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_generic_200_response)

        bruin_repository._nats_client.request.return_value = response_msg

        response = await bruin_repository.send_forward_email_milestone_notification(ticket_id, service_number)

        bruin_repository.post_notification_email_milestone.assert_awaited_once_with(
            ticket_id, service_number, notification_type
        )
        assert response == bruin_generic_200_response

    @pytest.mark.asyncio
    async def post_notification_email_milestone_test(self, bruin_repository, bruin_generic_200_response):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketPIABDeviceLostPower-E-Mail"

        request = {
            "request_id": uuid_,
            "body": {"notification_type": notification_type, "ticket_id": ticket_id, "service_number": service_number},
        }
        encoded_request = to_json_bytes(request)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_generic_200_response)

        bruin_repository._nats_client.request.return_value = response_msg

        with uuid_mock:
            result = await bruin_repository.post_notification_email_milestone(
                ticket_id, service_number, notification_type
            )

            bruin_repository._nats_client.request.assert_awaited_once_with(
                "bruin.notification.email.milestone", encoded_request, timeout=90
            )
            bruin_repository._notifications_repository.send_slack_message.assert_not_awaited()
            assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def post_notification_email_milestone_with_request_failing_test(
        self, bruin_repository, make_post_notification_email_milestone_request
    ):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketPIABDeviceLostPower-E-Mail"

        request = make_post_notification_email_milestone_request(
            request_id=uuid_, ticket_id=ticket_id, service_number=service_number, notification_type=notification_type
        )
        encoded_request = to_json_bytes(request)

        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()
        slack_message = (
            f"An error occurred when sending email for ticket id {ticket_id}, "
            f"service_number {service_number} and notification type {notification_type}...-> "
        )

        with uuid_mock:
            result = await bruin_repository.post_notification_email_milestone(
                ticket_id, service_number, notification_type
            )

            bruin_repository._nats_client.request.assert_awaited_once_with(
                "bruin.notification.email.milestone", encoded_request, timeout=90
            )
            bruin_repository._notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
            assert result == nats_error_response

    @pytest.mark.asyncio
    async def post_notification_email_milestone_with_request_returning__non_2xx_status_test(
        self, bruin_repository, bruin_500_response, make_post_notification_email_milestone_request
    ):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketPIABDeviceLostPower-E-Mail"

        request = make_post_notification_email_milestone_request(
            request_id=uuid_, ticket_id=ticket_id, service_number=service_number, notification_type=notification_type
        )
        encoded_request = to_json_bytes(request)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)

        bruin_repository._notifications_repository.send_slack_message = AsyncMock()
        bruin_repository._nats_client.request.return_value = response_msg
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()
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

            bruin_repository._nats_client.request.assert_awaited_once_with(
                "bruin.notification.email.milestone", encoded_request, timeout=90
            )
            bruin_repository._notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
            assert result == bruin_500_response
