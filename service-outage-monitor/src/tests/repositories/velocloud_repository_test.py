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
    async def get_links_with_edge_info_default_rpc_timeout_test(self):
        host = 'mettel.velocloud.net'

        request = {
            'request_id': uuid_,
            'body': {
                'host': host,
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
            result = await velocloud_repository.get_links_with_edge_info(host)

        event_bus.rpc_request.assert_awaited_once_with("get.links.with.edge.info", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_rpc_request_failing_test(self):
        host = 'mettel.velocloud.net'

        request = {
            'request_id': uuid_,
            'body': {
                'host': host,
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
            result = await velocloud_repository.get_links_with_edge_info(host)

        event_bus.rpc_request.assert_awaited_once_with("get.links.with.edge.info", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_edges_with_rpc_request_returning_non_2xx_status_test(self):
        host = 'mettel.velocloud.net'

        request = {
            'request_id': uuid_,
            'body': {
                'host': host,
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
            result = await velocloud_repository.get_links_with_edge_info(host)

        event_bus.rpc_request.assert_awaited_once_with("get.links.with.edge.info", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_edge_events_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        current_moment = datetime.now()
        past_moment = current_moment - timedelta(hours=1)
        future_moment = current_moment + timedelta(hours=1)
        event_types_filter = ['LINK_ALIVE', 'LINK_DEAD']

        request = {
            'request_id': uuid_,
            'body': {
                'edge': edge_full_id,
                'start_date': past_moment,
                'end_date': future_moment,
                'filter': event_types_filter,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {
                    'event': 'LINK_ALIVE',
                    'category': 'NETWORK',
                    'eventTime': '2019-07-30 07:38:00+00:00',
                    'message': 'GE2 alive'
                }
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
            result = await velocloud_repository.get_edge_events(
                edge_full_id, past_moment, future_moment, event_types_filter
            )

        event_bus.rpc_request.assert_awaited_once_with("alert.request.event.edge", request, timeout=180)
        assert result == response

    @pytest.mark.asyncio
    async def get_edge_events_with_no_event_types_filter_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        current_moment = datetime.now()
        past_moment = current_moment - timedelta(hours=1)
        future_moment = current_moment + timedelta(hours=1)
        event_types_filter = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']

        request = {
            'request_id': uuid_,
            'body': {
                'edge': edge_full_id,
                'start_date': past_moment,
                'end_date': future_moment,
                'filter': event_types_filter,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {
                    'event': 'LINK_ALIVE',
                    'category': 'NETWORK',
                    'eventTime': '2019-07-30 07:38:00+00:00',
                    'message': 'GE2 alive'
                }
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
            result = await velocloud_repository.get_edge_events(edge_full_id, past_moment, future_moment)

        event_bus.rpc_request.assert_awaited_once_with("alert.request.event.edge", request, timeout=180)
        assert result == response

    @pytest.mark.asyncio
    async def get_edge_events_with_rpc_request_failing_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        current_moment = datetime.now()
        past_moment = current_moment - timedelta(hours=1)
        future_moment = current_moment + timedelta(hours=1)
        event_types_filter = ['LINK_ALIVE', 'LINK_DEAD']

        request = {
            'request_id': uuid_,
            'body': {
                'edge': edge_full_id,
                'start_date': past_moment,
                'end_date': future_moment,
                'filter': event_types_filter,
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
            result = await velocloud_repository.get_edge_events(
                edge_full_id, past_moment, future_moment, event_types_filter
            )

        event_bus.rpc_request.assert_awaited_once_with("alert.request.event.edge", request, timeout=180)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_edge_events_with_rpc_request_returning_non_2xx_status_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        current_moment = datetime.now()
        past_moment = current_moment - timedelta(hours=1)
        future_moment = current_moment + timedelta(hours=1)
        event_types_filter = ['LINK_ALIVE', 'LINK_DEAD']

        request = {
            'request_id': uuid_,
            'body': {
                'edge': edge_full_id,
                'start_date': past_moment,
                'end_date': future_moment,
                'filter': event_types_filter,
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
            result = await velocloud_repository.get_edge_events(
                edge_full_id, past_moment, future_moment, event_types_filter
            )

        event_bus.rpc_request.assert_awaited_once_with("alert.request.event.edge", request, timeout=180)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_edges_for_triage_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        host = config.TRIAGE_CONFIG['velo_hosts']

        edge_list = 'edge'
        full_edge_list = [edge_list, edge_list, edge_list]
        edge_return = {'body': [edge_list], 'status': 200}
        edge_return_fail = {'body': 'Fail', 'status': 500}
        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_links_with_edge_info = CoroutineMock(side_effect=[edge_return, edge_return_fail,
                                                                      edge_return, edge_return])
        velocloud_repository.group_links_by_edge = Mock()

        with uuid_mock:
            await velocloud_repository.get_edges_for_triage()

        velocloud_repository.get_links_with_edge_info.assert_awaited()
        velocloud_repository.group_links_by_edge.assert_called_once_with(full_edge_list)

    @pytest.mark.asyncio
    async def get_last_edge_events_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        current_datetime = datetime.now()
        past_moment = current_datetime - timedelta(hours=1)
        event_types_filter = ['LINK_ALIVE', 'LINK_DEAD']

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_edge_events = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
            with uuid_mock:
                await velocloud_repository.get_last_edge_events(
                    edge_full_id, since=past_moment, event_types=event_types_filter
                )

        velocloud_repository.get_edge_events.assert_awaited_once_with(
            edge_full_id, from_=past_moment, to=current_datetime, event_types=event_types_filter,
        )

    @pytest.mark.asyncio
    async def get_last_down_edge_events_test(self):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}
        current_datetime = datetime.now()
        past_moment = current_datetime - timedelta(hours=1)
        event_types_filter = ['EDGE_DOWN', 'LINK_DEAD']

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_last_edge_events = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
            with uuid_mock:
                await velocloud_repository.get_last_down_edge_events(edge_full_id, since=past_moment)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment, event_types=event_types_filter,
        )

    def group_links_by_edge_test(self):
        edge_1_info = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
        }
        edge_2_info = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Sarif Industries',
            'enterpriseId': 2,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Adam Jensen',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
        }

        edge_1_link_1_info = {
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'REX',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        edge_1_link_2_info = {
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'RAY',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        link_1_with_edge_1_info = {
            **edge_1_info,
            **edge_1_link_1_info,
        }
        link_2_with_edge_1_info = {
            **edge_1_info,
            **edge_1_link_2_info,
        }

        edge_2_link_1_info = {
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'Augmented',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        edge_2_link_2_info = {
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'Lawrence Barrett',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        link_1_with_edge_2_info = {
            **edge_2_info,
            **edge_2_link_1_info,
        }
        link_2_with_edge_2_info = {
            **edge_2_info,
            **edge_2_link_2_info,
        }

        invalid_link_with_edge_info = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Sarif Industries',
            'enterpriseId': 2,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': None,
            'edgeState': None,
            'edgeSystemUpSince': None,
            'edgeServiceUpSince': None,
            'edgeLastContact': None,
            'edgeId': None,
            'edgeSerialNumber': None,
            'edgeHASerialNumber': None,
            'edgeModelNumber': None,
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': None,
            'isp': None,
            'interface': None,
            'internalId': None,
            'linkState': None,
            'linkLastActive': None,
            'linkVpnState': None,
            'linkId': None,
            'linkIpAddress': None,
        }

        links_with_edge_info = [
            link_1_with_edge_1_info,
            link_2_with_edge_1_info,
            link_1_with_edge_2_info,
            link_2_with_edge_2_info,
            invalid_link_with_edge_info,
        ]

        result = VelocloudRepository.group_links_by_edge(links_with_edge_info)

        expected = [
            {
                **edge_1_info,
                'links': [
                    edge_1_link_1_info,
                    edge_1_link_2_info,
                ],
            },
            {
                **edge_2_info,
                'links': [
                    edge_2_link_1_info,
                    edge_2_link_2_info,
                ],
            },
        ]

        assert result == expected
