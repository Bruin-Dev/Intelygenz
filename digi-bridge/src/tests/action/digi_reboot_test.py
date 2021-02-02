from unittest.mock import Mock

import pytest
from application.actions.digi_reboot import DiGiReboot
from asynctest import CoroutineMock


class TestDiGiReboot:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        digi_repository = Mock()

        digi_reboot = DiGiReboot(logger, event_bus, digi_repository)

        assert digi_reboot._logger == logger
        assert digi_reboot._event_bus == event_bus
        assert digi_reboot._digi_repository == digi_repository

    @pytest.mark.asyncio
    async def digi_reboot_test(self):
        msg = {'request_id': '123',
               'response_topic': '231',
               'body': {
                        'velo_serial': 'VC05200046188',
                        'ticket': '3574667',
                        'MAC': '00:04:2d:0b:cf:7f:0000'}
               }

        reboot_return = {
                          'body': [{'Message': 'Success'}],
                          'status': 200
        }
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        digi_repository = Mock()
        digi_repository.reboot = CoroutineMock(return_value=reboot_return)

        digi_reboot = DiGiReboot(logger, event_bus, digi_repository)

        await digi_reboot.digi_reboot(msg)

        digi_repository.reboot.assert_awaited_once_with(msg['request_id'], msg['body'])
        event_bus.publish_message.assert_awaited_once_with(msg['response_topic'], dict(request_id=msg['request_id'],
                                                                                       body=reboot_return['body'],
                                                                                       status=reboot_return['status']))

    @pytest.mark.asyncio
    async def digi_reboot_no_body_test(self):
        msg = {'request_id': '123',
               'response_topic': '231'}
        error_message = 'Must include "body" in request'

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        digi_repository = Mock()
        digi_repository.reboot = CoroutineMock()

        digi_reboot = DiGiReboot(logger, event_bus, digi_repository)

        await digi_reboot.digi_reboot(msg)

        digi_repository.reboot.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(msg['response_topic'], dict(request_id=msg['request_id'],
                                                                                       body=error_message,
                                                                                       status=400))

    @pytest.mark.asyncio
    async def digi_reboot_empty_body_test(self):
        msg = {'request_id': '123',
               'response_topic': '231',
               'body': {}}
        error_message = 'You must include "velo_serial", "ticket", "MAC" ' \
                        'in the "body" field of the response request'

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        digi_repository = Mock()
        digi_repository.reboot = CoroutineMock()

        digi_reboot = DiGiReboot(logger, event_bus, digi_repository)

        await digi_reboot.digi_reboot(msg)

        digi_repository.reboot.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(msg['response_topic'], dict(request_id=msg['request_id'],
                                                                                       body=error_message,
                                                                                       status=400))
