import asyncio
import pytest

from datetime import datetime, timedelta
from unittest.mock import Mock, patch, call
from shortuuid import uuid
from asynctest import CoroutineMock

from application.repositories import velocloud_repository as velocloud_repository_module
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
    async def get_links_metrics_by_host_test(self):
        host = 'some-host'
        interval = {'start': 'date_start', 'end': 'date_end'}
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
            result = await velocloud_repository.get_links_metrics_by_host(host, interval)

        assert result == response

    @pytest.mark.asyncio
    async def get_links_metrics_by_host_bad_status_test(self):
        host = 'some-host'
        interval = {'start': 'date_start', 'end': 'date_end'}
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
            result = await velocloud_repository.get_links_metrics_by_host(host, interval)

        assert result == response

    @pytest.mark.asyncio
    async def get_links_metrics_by_host_exception_test(self):
        host = 'some-host'
        interval = {'start': 'date_start', 'end': 'date_end'}
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[Exception, None])

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await velocloud_repository.get_links_metrics_by_host(host, interval)

        assert result == {'body': None, 'status': 503}

    @pytest.mark.asyncio
    async def get_all_links_metrics_test(self):
        host = 'some-host'
        interval = {'start': 'date_start', 'end': 'date_end'}
        response_1 = {
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
        response_2 = {
            'request_id': uuid_,
            'body': [
            ],
            'status': 400,
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_links_metrics_by_host = CoroutineMock(side_effect=[response_1, response_2])

        with uuid_mock:
            result = await velocloud_repository.get_all_links_metrics(interval)

        assert result == response_1

    @pytest.mark.asyncio
    async def get_links_metrics_for_latency_checks_test(self):
        host = 'some-host'
        next_run_time = datetime.now()
        past_moment = next_run_time - timedelta(
            minutes=testconfig.MONITOR_CONFIG['monitoring_minutes_per_trouble']['latency']
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        response_1 = {
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

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_all_links_metrics = CoroutineMock(return_value=response_1)

        with uuid_mock:
            with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
                result = await velocloud_repository.get_links_metrics_for_latency_checks()

        assert result == response_1
        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(
            interval={'start': past_moment, 'end': next_run_time})

    @pytest.mark.asyncio
    async def get_links_metrics_for_packet_loss_checks_test(self):
        host = 'some-host'
        next_run_time = datetime.now()
        past_moment = next_run_time - timedelta(
            minutes=testconfig.MONITOR_CONFIG['monitoring_minutes_per_trouble']['packet_loss']
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        response_1 = {
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

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_all_links_metrics = CoroutineMock(return_value=response_1)

        with uuid_mock:
            with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
                result = await velocloud_repository.get_links_metrics_for_packet_loss_checks()

        assert result == response_1
        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(
            interval={'start': past_moment, 'end': next_run_time})

    @pytest.mark.asyncio
    async def get_links_metrics_for_jitter_checks_test(self):
        host = 'some-host'
        next_run_time = datetime.now()
        past_moment = next_run_time - timedelta(
            minutes=testconfig.MONITOR_CONFIG['monitoring_minutes_per_trouble']['jitter']
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        response_1 = {
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

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_all_links_metrics = CoroutineMock(return_value=response_1)

        with uuid_mock:
            with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
                result = await velocloud_repository.get_links_metrics_for_jitter_checks()

        assert result == response_1
        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(
            interval={'start': past_moment, 'end': next_run_time})

    @pytest.mark.asyncio
    async def get_links_metrics_for_bandwidth_checks_test(self):
        host = 'some-host'
        next_run_time = datetime.now()
        past_moment = next_run_time - timedelta(
            minutes=testconfig.MONITOR_CONFIG['monitoring_minutes_per_trouble']['bandwidth']
        )
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        response_1 = {
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

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_all_links_metrics = CoroutineMock(return_value=response_1)

        with uuid_mock:
            with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
                result = await velocloud_repository.get_links_metrics_for_bandwidth_checks()

        assert result == response_1
        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(
            interval={'start': past_moment, 'end': next_run_time})

    @pytest.mark.asyncio
    async def get_links_metrics_for_autoresolve_test(self):
        current_moment = datetime.now()
        past_moment = current_moment - timedelta(
            minutes=testconfig.MONITOR_CONFIG['autoresolve']['metrics_lookup_interval_minutes']
        )

        links_metrics_response = {
            'request_id': uuid_,
            'body': [
                {
                    'linkId': 22,
                    'bytesTx': 5694196,
                    'bytesRx': 9607567,
                    'packetsTx': 81966,
                    'packetsRx': 95687,
                    'totalBytes': 15301763,
                    'totalPackets': 177653,
                    'p1BytesRx': 35503,
                    'p1BytesTx': 3279,
                    'p1PacketsRx': 168,
                    'p1PacketsTx': 46,
                    'p2BytesRx': 4720158,
                    'p2BytesTx': 0,
                    'p2PacketsRx': 18879,
                    'p2PacketsTx': 0,
                    'p3BytesRx': 0,
                    'p3BytesTx': 0,
                    'p3PacketsRx': 0,
                    'p3PacketsTx': 0,
                    'controlBytesRx': 4851906,
                    'controlBytesTx': 5690917,
                    'controlPacketsRx': 76640,
                    'controlPacketsTx': 81920,
                    'bpsOfBestPathRx': 182296000,
                    'bpsOfBestPathTx': 43243000,
                    'bestJitterMsRx': 0,
                    'bestJitterMsTx': 0,
                    'bestLatencyMsRx': 3,
                    'bestLatencyMsTx': 6.4167,
                    'bestLossPctRx': 0,
                    'bestLossPctTx': 0,
                    'scoreTx': 4.400000095367432,
                    'scoreRx': 4.400000095367432,
                    'signalStrength': 0,
                    'state': 0,
                    'name': 'REX',
                    'link': {
                        'host': 'mettel.velocloud.net',
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
                    },
                }
            ],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)
        velocloud_repository.get_all_links_metrics = CoroutineMock(return_value=links_metrics_response)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_moment)

        with uuid_mock:
            with patch.object(velocloud_repository_module, 'datetime', new=datetime_mock):
                result = await velocloud_repository.get_links_metrics_for_autoresolve()

        assert result == links_metrics_response
        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(
            interval={'start': past_moment, 'end': current_moment},
        )
