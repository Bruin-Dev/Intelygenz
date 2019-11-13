import json
from unittest.mock import Mock

import pytest
from application.actions.get_affecting_ticket_details_by_edge_serial import GetAffectingTicketDetailsByEdgeSerial
from asynctest import CoroutineMock


class TestGetAffectingTicketDetailsByEdgeSerial:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        ticket_details = GetAffectingTicketDetailsByEdgeSerial(logger, event_bus, bruin_repository)

        assert ticket_details._logger is logger
        assert ticket_details._event_bus is event_bus
        assert ticket_details._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_affecting_ticket_details_by_edge_serial_test(self):
        logger = Mock()

        request_id = "123"
        response_topic = 'some.random.rpc.inbox'
        client_id = 123
        edge_serial = 'VC05200026138'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'edge_serial': edge_serial,
            'client_id': client_id,
        }
        ticket_1_id = 321
        ticket_2_id = 456
        ticket_1_details = {
            'ticketID': ticket_1_id,
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
        ticket_2_details = {
            'ticketID': ticket_2_id,
            'ticketDetails': [
                {
                    "detailID": 2746938,
                    "detailValue": edge_serial,
                },
            ],
            'ticketNotes': [
                {
                    "noteId": 41894042,
                    "noteValue": f'#*Automation Engine*# \n TimeStamp: 2019-07-30 09:38:00+00:00',
                }
            ],
        }
        ticket_details_list = [ticket_1_details, ticket_2_details]
        get_ticket_details_response = {
            'request_id': request_id,
            'ticket_details_list': ticket_details_list,
            'status': 200,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_affecting_ticket_details_by_edge_serial = Mock(return_value=ticket_details_list)

        ticket_details = GetAffectingTicketDetailsByEdgeSerial(logger, event_bus, bruin_repository)
        await ticket_details.send_affecting_ticket_details_by_edge_serial(json.dumps(msg))

        ticket_details._bruin_repository.get_affecting_ticket_details_by_edge_serial.assert_called_once_with(
            edge_serial=edge_serial, client_id=client_id,
        )
        ticket_details._event_bus.publish_message.assert_awaited_once_with(
            response_topic, json.dumps(get_ticket_details_response)
        )

    @pytest.mark.asyncio
    async def get_affecting_ticket_details_by_edge_serial_with_no_details_found_test(self):
        logger = Mock()

        request_id = "123"
        response_topic = 'some.random.rpc.inbox'
        client_id = 123
        edge_serial = 'VC05200026138'
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'edge_serial': edge_serial,
            'client_id': client_id,
        }
        ticket_details_list = []
        get_ticket_details_response = {
            'request_id': request_id,
            'ticket_details_list': ticket_details_list,
            'status': 500,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_affecting_ticket_details_by_edge_serial = Mock(return_value=ticket_details_list)

        ticket_details = GetAffectingTicketDetailsByEdgeSerial(logger, event_bus, bruin_repository)
        await ticket_details.send_affecting_ticket_details_by_edge_serial(json.dumps(msg))

        ticket_details._bruin_repository.get_affecting_ticket_details_by_edge_serial.assert_called_once_with(
            edge_serial=edge_serial, client_id=client_id,
        )
        ticket_details._event_bus.publish_message.assert_awaited_once_with(
            response_topic, json.dumps(get_ticket_details_response)
        )
