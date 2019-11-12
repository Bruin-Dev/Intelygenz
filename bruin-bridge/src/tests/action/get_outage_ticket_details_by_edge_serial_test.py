import json
from unittest.mock import Mock

import pytest
from application.actions.get_outage_ticket_details_by_edge_serial import GetOutageTicketDetailsByEdgeSerial
from asynctest import CoroutineMock


class TestGetTicketDetailsByEdgeSerial:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        ticket_details = GetOutageTicketDetailsByEdgeSerial(logger, event_bus, bruin_repository)

        assert ticket_details._logger is logger
        assert ticket_details._event_bus is event_bus
        assert ticket_details._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_outage_ticket_details_by_edge_serial_test(self):
        logger = Mock()

        request_id = "123"
        response_topic = 'some.random.rpc.inbox'
        ticket_id = 321
        client_id = 123
        edge_serial = 'VC05200026138'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'edge_serial': edge_serial,
            'client_id': client_id,
        }
        ticket_details = {
            'ticketID': ticket_id,
            'ticketDetails': [
                {
                    "detailID": 2746937,
                    "detailValue": edge_serial,
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894041,
                    "noteValue": f'#*Automation Engine*# \n TimeStamp: 2019-07-30 06:38:00+00:00',
                }
            ],
        }
        get_ticket_details_response = {
            'request_id': request_id,
            'ticket_details': ticket_details,
            'status': 200,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_outage_ticket_details_by_edge_serial = Mock(return_value=ticket_details)

        outage_ticket_details = GetOutageTicketDetailsByEdgeSerial(logger, event_bus, bruin_repository)
        await outage_ticket_details.send_outage_ticket_details_by_edge_serial(json.dumps(msg))

        outage_ticket_details._bruin_repository.get_outage_ticket_details_by_edge_serial.assert_called_once_with(
            edge_serial=edge_serial, client_id=client_id,
        )
        outage_ticket_details._event_bus.publish_message.assert_awaited_once_with(
            response_topic, json.dumps(get_ticket_details_response)
        )

    @pytest.mark.asyncio
    async def get_outage_ticket_details_by_edge_serial_with_no_details_found_test(self):
        logger = Mock()

        request_id = "123"
        response_topic = 'some.random.rpc.inbox'
        ticket_id = None
        client_id = 123
        edge_serial = 'VC05200026138'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'edge_serial': edge_serial,
            'client_id': client_id,
        }
        ticket_details = None
        get_ticket_details_response = {
            'request_id': request_id,
            'ticket_details': ticket_details,
            'status': 500,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_outage_ticket_details_by_edge_serial = Mock(return_value=ticket_details)

        outage_ticket_details = GetOutageTicketDetailsByEdgeSerial(logger, event_bus, bruin_repository)
        await outage_ticket_details.send_outage_ticket_details_by_edge_serial(json.dumps(msg))

        outage_ticket_details._bruin_repository.get_outage_ticket_details_by_edge_serial.assert_called_once_with(
            edge_serial=edge_serial, client_id=client_id,
        )
        outage_ticket_details._event_bus.publish_message.assert_awaited_once_with(
            response_topic, json.dumps(get_ticket_details_response)
        )
