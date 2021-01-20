import os
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.repositories.digi_repository import DiGiRepository
from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import digi_repository as digi_repository_module
from application.repositories import nats_error_response
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(digi_repository_module, 'uuid', return_value=uuid_)


class TestDiGiRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        digi_repository = DiGiRepository(event_bus, logger, config, notifications_repository)

        assert digi_repository._event_bus is event_bus
        assert digi_repository._logger is logger
        assert digi_repository._config is config
        assert digi_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def reboot_link_success_test(self):
        ticket_id = 11111
        service_number = 'VC1234567'
        logical_id = '00:04:2d:123'
        request = {
            'request_id': uuid_,
            'body': {
                'velo_serial': service_number,
                'ticket': ticket_id,
                'MAC': logical_id
            },
        }
        return_body = {
            'body': 'Success',
            'status': 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=return_body)

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        digi_repository = DiGiRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await digi_repository.reboot_link(service_number, ticket_id, logical_id)

        event_bus.rpc_request.assert_awaited_once_with("digi.reboot", request, timeout=90)
        assert result == return_body

    @pytest.mark.asyncio
    async def reboot_link_success_with_rpc_request_failing_test(self):
        ticket_id = 11111
        service_number = 'VC1234567'
        logical_id = '00:04:2d:123'
        request = {
            'request_id': uuid_,
            'body': {
                'velo_serial': service_number,
                'ticket': ticket_id,
                'MAC': logical_id
            },
        }
        return_body = {
            'body': 'Success',
            'status': 200
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        digi_repository = DiGiRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await digi_repository.reboot_link(service_number, ticket_id, logical_id)

        event_bus.rpc_request.assert_awaited_once_with("digi.reboot", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def reboot_link_success_with_non_2xx_status_test(self):
        ticket_id = 11111
        service_number = 'VC1234567'
        logical_id = '00:04:2d:123'
        request = {
            'request_id': uuid_,
            'body': {
                'velo_serial': service_number,
                'ticket': ticket_id,
                'MAC': logical_id
            },
        }
        return_body = {
            'body': 'Failed',
            'status': 400
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=return_body)

        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        digi_repository = DiGiRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await digi_repository.reboot_link(service_number, ticket_id, logical_id)

        event_bus.rpc_request.assert_awaited_once_with("digi.reboot", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == return_body
