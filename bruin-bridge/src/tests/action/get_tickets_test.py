from unittest.mock import Mock

import pytest
from application.actions.get_tickets import GetTicket
from asynctest import CoroutineMock

from config import testconfig as config


class TestGetTicket:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)

        assert bruin_ticket_response._logger is logger
        assert bruin_ticket_response._config is config.BRUIN_CONFIG
        assert bruin_ticket_response._event_bus is event_bus
        assert bruin_ticket_response._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_all_tickets_with_ticket_id_defined_in_msg_200_test(self):
        logger = Mock()
        filtered_tickets_list = [{'ticketID': 123}, {'ticketID': 321}]
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        client_id = 123
        ticket_id = 321

        category = 'SD-WAN'
        ticket_topic = 'VOO'

        ticket_status_list = ['New', 'In-Progress']
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                'client_id': client_id,
                'ticket_id': ticket_id,
                'category': category,
                'ticket_topic': ticket_topic,
                'ticket_status': ticket_status_list,
            },
        }
        response_to_publish_in_topic = {
            'request_id': request_id,
            'body': filtered_tickets_list,
            'status': 200
        }
        param_copy = msg['body'].copy()
        del [param_copy['ticket_status']]

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = CoroutineMock(return_value={'body': filtered_tickets_list,
                                                                                'status': 200})

        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_all_tickets(msg)

        bruin_ticket_response._bruin_repository.get_all_filtered_tickets.assert_awaited_once_with(
            param_copy, ticket_status_list
        )
        bruin_ticket_response._event_bus.publish_message.assert_awaited_once_with(
            response_topic, response_to_publish_in_topic
        )

    @pytest.mark.asyncio
    async def get_all_tickets_with_no_ticket_id_test(self):
        logger = Mock()
        filtered_tickets_list = [{'ticketID': 123}, {'ticketID': 321}]
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        client_id = 123

        category = 'SD-WAN'
        ticket_topic = 'VOO'

        ticket_status_list = ['New', 'In-Progress']
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                'client_id': client_id,
                'category': category,
                'ticket_topic': ticket_topic,
                'ticket_status': ticket_status_list,
            },
        }
        param_copy = msg['body'].copy()
        del [param_copy['ticket_status']]
        param_copy['ticket_id'] = ''
        response_to_publish_in_topic = {
            'request_id': request_id,
            'body': filtered_tickets_list,
            'status': 200
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = CoroutineMock(return_value={'body': filtered_tickets_list,
                                                                                'status': 200})

        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_all_tickets(msg)

        bruin_ticket_response._bruin_repository.get_all_filtered_tickets.assert_awaited_once_with(
            param_copy, ticket_status_list
        )
        bruin_ticket_response._event_bus.publish_message.assert_awaited_once_with(
            response_topic, response_to_publish_in_topic
        )

    @pytest.mark.asyncio
    async def get_tickets_with_date_test(self):
        logger = Mock()
        client_id = 123

        filtered_tickets_list = [
            {'clientID': client_id, 'clientName': 'Sterling Jewelers, Inc.', 'ticketID': 4767858, 'category': 'SD-WAN',
             'topic': 'Service Outage Trouble', 'referenceTicketNumber': 0, 'ticketStatus': 'New',
             'createDate': '8/20/2020 3:31:00 AM', 'createdBy': 'Intelygenz Ai',
             'creationNote': None, 'resolveDate': '', 'resolvedby': None, 'closeDate': None, 'closedBy': None,
             'lastUpdate': None, 'updatedBy': None, 'mostRecentNote': '8/20/2020 3:31:03 AM Intelygenz Ai',
             'nextScheduledDate': '8/26/2020 4:00:00 AM', 'flags': '', 'severity': '2'},
            {'clientID': client_id, 'clientName': 'Sterling Jewelers, Inc.', 'ticketID': 4767346,
             'category': 'SIP Trunking', 'topic': 'Service Outage Trouble', 'referenceTicketNumber': 0,
             'ticketStatus': 'In-Progress',
             'createDate': '8/19/2020 8:13:00 PM', 'createdBy': 'Jerald Beard',
             'creationNote': None, 'resolveDate': '', 'resolvedby': None, 'closeDate': None, 'closedBy': None,
             'lastUpdate': None, 'updatedBy': None, 'mostRecentNote': '8/19/2020 9:17:19 PM Richard Jordan',
             'nextScheduledDate': '8/21/2020 5:11:42 AM', 'flags': 'Frozen,Frozen', 'severity': '2'}]

        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        category = 'SD-WAN'
        ticket_topic = 'VOO'

        ticket_status_list = ['New', 'In-Progress']
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                'client_id': client_id,
                'category': category,
                'ticket_topic': ticket_topic,
                'ticket_status': ticket_status_list,
                'start_date': "2020-8-19T20:12:00Z",
                'end_date': "2020-8-20T20:12:00Z"
            },
        }
        param_copy = msg['body'].copy()
        del [param_copy['ticket_status']]
        param_copy['ticket_id'] = ''
        response_to_publish_in_topic = {
            'request_id': request_id,
            'body': filtered_tickets_list,
            'status': 200
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = CoroutineMock(return_value={'body': filtered_tickets_list,
                                                                                'status': 200})

        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_all_tickets(msg)

        bruin_ticket_response._bruin_repository.get_all_filtered_tickets.assert_awaited_once_with(
            param_copy, ticket_status_list
        )
        bruin_ticket_response._event_bus.publish_message.assert_awaited_once_with(
            response_topic, response_to_publish_in_topic
        )

    @pytest.mark.asyncio
    async def get_all_tickets_missing_keys_in_params_test(self):
        logger = Mock()
        filtered_tickets_list = [{'ticketID': 123}, {'ticketID': 321}]
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        category = 'SD-WAN'
        ticket_topic = 'VOO'

        ticket_status_list = ['New', 'In-Progress']
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
            'body': {
                'category': category,
                'ticket_topic': ticket_topic,
                'ticket_status': ticket_status_list,
            },
        }

        response_to_publish_in_topic = {
            'request_id': request_id,
            'body': 'You must specify '
                    '{..."body:{"client_id", "category", "ticket_topic",'
                    ' "ticket_status":[list of statuses]}...} in the request',
            'status': 400
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = CoroutineMock(return_value={'body': filtered_tickets_list,
                                                                                'status': 200})

        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_all_tickets(msg)

        bruin_ticket_response._bruin_repository.get_all_filtered_tickets.assert_not_awaited()
        bruin_ticket_response._event_bus.publish_message.assert_awaited_once_with(
            response_topic, response_to_publish_in_topic
        )

    @pytest.mark.asyncio
    async def get_all_tickets_missing_body_test(self):
        logger = Mock()
        filtered_tickets_list = [{'ticketID': 123}, {'ticketID': 321}]
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        ticket_status_list = ['New', 'In-Progress']
        msg = {
            'request_id': request_id,
            'response_topic': response_topic,
        }

        response_to_publish_in_topic = {
            'request_id': request_id,
            'body': 'Must include "body" in request',
            'status': 400
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_all_filtered_tickets = CoroutineMock(return_value={'body': filtered_tickets_list,
                                                                                'status': 200})

        bruin_ticket_response = GetTicket(logger, config.BRUIN_CONFIG, event_bus, bruin_repository)
        await bruin_ticket_response.get_all_tickets(msg)

        bruin_ticket_response._bruin_repository.get_all_filtered_tickets.assert_not_awaited()
        bruin_ticket_response._event_bus.publish_message.assert_awaited_once_with(
            response_topic, response_to_publish_in_topic
        )
