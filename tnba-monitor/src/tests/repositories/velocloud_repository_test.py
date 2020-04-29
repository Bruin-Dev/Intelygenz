from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories import nats_error_response
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, 'uuid', return_value=uuid_)


class TestVelocloudRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is config
        assert velocloud_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_edges_with_default_rpc_timeout_test(self):
        filter_ = {'mettel.velocloud.net': []}

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
            ],
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository.get_edges(filter_)

        event_bus.rpc_request.assert_awaited_once_with("edge.list.request", request, timeout=300)
        assert result == response

    @pytest.mark.asyncio
    async def get_edges_with_custom_rpc_timeout_test(self):
        filter_ = {'mettel.velocloud.net': []}
        rpc_timeout = 1000

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
            ],
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository.get_edges(filter_, rpc_timeout=rpc_timeout)

        event_bus.rpc_request.assert_awaited_once_with("edge.list.request", request, timeout=rpc_timeout)
        assert result == response

    @pytest.mark.asyncio
    async def get_edges_with_no_filter_specified_test(self):
        filter_ = {}

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
                {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
            ],
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository.get_edges()

        event_bus.rpc_request.assert_awaited_once_with("edge.list.request", request, timeout=300)
        assert result == response

    @pytest.mark.asyncio
    async def get_edges_with_rpc_request_failing_test(self):
        filter_ = {'mettel.velocloud.net': []}

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository.get_edges(filter_)

        event_bus.rpc_request.assert_awaited_once_with("edge.list.request", request, timeout=300)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_edges_with_rpc_request_returning_non_2xx_status_test(self):
        filter_ = {'mettel.velocloud.net': []}

        request = {
            'request_id': uuid_,
            'body': {
                'filter': filter_,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository.get_edges(filter_)

        event_bus.rpc_request.assert_awaited_once_with("edge.list.request", request, timeout=300)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_edge_status_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        request = {
            'request_id': uuid_,
            'body': edge_full_id,
        }
        response = {
            'request_id': uuid_,
            'body': {
                'edge_id': edge_full_id,
                'edge_info': {
                    'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
                    'links': [
                        {'linkId': 1234, 'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                        {'linkId': 5678, 'link': {'state': 'STABLE', 'interface': 'GE2'}},
                    ],
                    'enterprise_name': 'EVIL-CORP|12345|',
                }
            },
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository.get_edge_status(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with("edge.status.request", request, timeout=120)
        assert result == response

    @pytest.mark.asyncio
    async def get_edge_status_with_rpc_request_failing_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        request = {
            'request_id': uuid_,
            'body': edge_full_id,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository.get_edge_status(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with("edge.status.request", request, timeout=120)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_edge_status_with_rpc_request_returning_non_2xx_status_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        request = {
            'request_id': uuid_,
            'body': edge_full_id,
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository.get_edge_status(edge_full_id)

        event_bus.rpc_request.assert_awaited_once_with("edge.status.request", request, timeout=120)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_edges_for_tnba_monitoring_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        filter_ = config.MONITOR_CONFIG['velo_filter']

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_edges = CoroutineMock()

        with uuid_mock:
            await velocloud_repository.get_edges_for_tnba_monitoring()

        velocloud_repository.get_edges.assert_awaited_once_with(filter_=filter_)
