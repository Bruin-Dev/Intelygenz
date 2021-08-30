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
    async def get_enterprise_events_test(self):
        enterprise_id = 1
        current_moment = datetime.now()
        past_moment = current_moment - timedelta(hours=1)
        future_moment = current_moment + timedelta(hours=1)
        event_types_filter = ['EDGE_DOWN', 'LINK_DEAD']

        request = {
            'request_id': uuid_,
            'body': {
                'enterprise_id': enterprise_id,
                'host': testconfig.BOUNCING_DETECTOR_CONFIG['velocloud_host'],
                'start_date': past_moment,
                'end_date': future_moment,
                'filter': event_types_filter,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {
                    'event': 'LINK_DEAD',
                    'category': 'NETWORK',
                    'eventTime': '2019-07-30 07:38:00+00:00',
                    'message': 'GE2 dead'
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
            result = await velocloud_repository._get_enterprise_events(
                enterprise_id, past_moment, future_moment
            )

        event_bus.rpc_request.assert_awaited_once_with("alert.request.event.enterprise", request, timeout=180)
        assert result == response

    @pytest.mark.asyncio
    async def get_enterprise_events_with_rpc_request_failing_test(self):
        enterprise_id = 1
        current_moment = datetime.now()
        past_moment = current_moment - timedelta(hours=1)
        future_moment = current_moment + timedelta(hours=1)
        event_types_filter = ['EDGE_DOWN', 'LINK_DEAD']

        request = {
            'request_id': uuid_,
            'body': {
                'enterprise_id': enterprise_id,
                'host': testconfig.BOUNCING_DETECTOR_CONFIG['velocloud_host'],
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
            result = await velocloud_repository._get_enterprise_events(
                enterprise_id, past_moment, future_moment
            )

        event_bus.rpc_request.assert_awaited_once_with("alert.request.event.enterprise", request, timeout=180)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_enterprise_events_with_rpc_request_returning_non_2xx_status_test(self):
        enterprise_id = 1
        current_moment = datetime.now()
        past_moment = current_moment - timedelta(hours=1)
        future_moment = current_moment + timedelta(hours=1)
        event_types_filter = ['EDGE_DOWN', 'LINK_DEAD']

        request = {
            'request_id': uuid_,
            'body': {
                'enterprise_id': enterprise_id,
                'host': testconfig.BOUNCING_DETECTOR_CONFIG['velocloud_host'],
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
            result = await velocloud_repository._get_enterprise_events(
                enterprise_id, past_moment, future_moment
            )

        event_bus.rpc_request.assert_awaited_once_with("alert.request.event.enterprise", request, timeout=180)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_last_enterprise_events_test(self):
        enterprise_id = 1
        current_datetime = datetime.now()
        past_moment = current_datetime - timedelta(hours=1)

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository._get_enterprise_events = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
            with uuid_mock:
                await velocloud_repository.get_last_enterprise_events(enterprise_id)

        velocloud_repository._get_enterprise_events.assert_awaited_once_with(
            enterprise_id, from_=past_moment, to=current_datetime,
        )

    @pytest.mark.asyncio
    async def get_links_metrics_test(self):
        host = 'some-host'
        interval = {'start': 'date_start', 'end': 'date_end'}
        request = {
            "request_id": uuid_,
            "body": {
                'host': host,
                'interval': interval,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {
                    'host': host,
                    'enterpriseName': 'Militaires Sans Frontières',
                    'enterpriseId': 2,
                    'enterpriseProxyId': None,
                    'enterpriseProxyName': None,
                    'edgeName': 'Big Boss',
                    'edgeState': 'CONNECTED',
                    'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
                    'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
                    'edgeLastContact': '2020-09-29T04:48:55.000Z',
                    'edgeId': 4206,
                    'edgeSerialNumber': 'VC05200048223',
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
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
            ],
            'status': 200,
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await velocloud_repository._get_links_metrics(host, interval)

        event_bus.rpc_request.assert_awaited_once_with("get.links.metric.info", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_links_metrics_bad_status_test(self):
        host = 'some-host'
        interval = {'start': 'date_start', 'end': 'date_end'}
        request = {
            "request_id": uuid_,
            "body": {
                'host': host,
                'interval': interval,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {
                    'host': host,
                    'enterpriseName': 'Militaires Sans Frontières',
                    'enterpriseId': 2,
                    'enterpriseProxyId': None,
                    'enterpriseProxyName': None,
                    'edgeName': 'Big Boss',
                    'edgeState': 'CONNECTED',
                    'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
                    'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
                    'edgeLastContact': '2020-09-29T04:48:55.000Z',
                    'edgeId': 4206,
                    'edgeSerialNumber': 'VC05200048223',
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
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
            ],
            'status': 400,
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await velocloud_repository._get_links_metrics(host, interval)

        event_bus.rpc_request.assert_awaited_once_with("get.links.metric.info", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_links_metrics_exception_test(self):
        host = 'some-host'
        interval = {'start': 'date_start', 'end': 'date_end'}
        request = {
            "request_id": uuid_,
            "body": {
                'host': host,
                'interval': interval,
            },
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[Exception, None])

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await velocloud_repository._get_links_metrics(host, interval)

        event_bus.rpc_request.assert_awaited_once_with("get.links.metric.info", request, timeout=30)
        assert result == {'body': None, 'status': 503}

    @pytest.mark.asyncio
    async def get_last_link_metrics_test(self):
        current_datetime = datetime.now()
        past_moment = current_datetime - timedelta(hours=1)
        interval = {'start': past_moment, 'end': current_datetime}

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository._get_links_metrics = CoroutineMock()

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
            with uuid_mock:
                await velocloud_repository.get_last_link_metrics()

        velocloud_repository._get_links_metrics.assert_awaited_once_with(
            testconfig.BOUNCING_DETECTOR_CONFIG['velocloud_host'],
            interval
        )
