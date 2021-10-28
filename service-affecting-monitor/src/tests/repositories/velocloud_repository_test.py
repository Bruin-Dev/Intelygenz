import pytest

from datetime import datetime, timedelta
from unittest.mock import patch
from shortuuid import uuid
from asynctest import CoroutineMock

from application import AffectingTroubles
from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories import nats_error_response
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, 'uuid', return_value=uuid_)


class TestVelocloudRepository:
    def instance_test(self, velocloud_repository, event_bus, logger, notifications_repository):
        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is testconfig
        assert velocloud_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_links_metrics_by_host__metrics_retrieved_test(
            self, velocloud_repository, make_get_links_metrics_request, make_metrics_for_link,
            make_list_of_link_metrics, make_rpc_response):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': datetime.now() - timedelta(minutes=30),
            'end': datetime.now(),
        }

        link_1_metrics = make_metrics_for_link(link_id=1)
        link_2_metrics = make_metrics_for_link(link_id=2)
        links_metrics = make_list_of_link_metrics(link_1_metrics, link_2_metrics)

        request = make_get_links_metrics_request(
            request_id=uuid_,
            velocloud_host=velocloud_host,
            interval=interval,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body=links_metrics,
            status=200,
        )

        velocloud_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await velocloud_repository.get_links_metrics_by_host(velocloud_host, interval)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.metric.info", request, timeout=30
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_links_metrics_by_host__rpc_request_failing_test(
            self, velocloud_repository, make_get_links_metrics_request):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': datetime.now() - timedelta(minutes=30),
            'end': datetime.now(),
        }

        request = make_get_links_metrics_request(
            request_id=uuid_,
            velocloud_host=velocloud_host,
            interval=interval,
        )

        velocloud_repository._event_bus.rpc_request.side_effect = Exception
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await velocloud_repository.get_links_metrics_by_host(velocloud_host, interval)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.metric.info", request, timeout=30
        )
        velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        velocloud_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_links_metrics_by_host__rpc_request_has_not_2xx_status_test(
            self, velocloud_repository, make_get_links_metrics_request, velocloud_500_response):
        velocloud_host = 'mettel.velocloud.net'
        interval = {
            'start': datetime.now() - timedelta(minutes=30),
            'end': datetime.now(),
        }

        request = make_get_links_metrics_request(
            request_id=uuid_,
            velocloud_host=velocloud_host,
            interval=interval,
        )

        velocloud_repository._event_bus.rpc_request.return_value = velocloud_500_response
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await velocloud_repository.get_links_metrics_by_host(velocloud_host, interval)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.metric.info", request, timeout=30
        )
        velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        velocloud_repository._logger.error.assert_called_once()
        assert result == velocloud_500_response

    @pytest.mark.asyncio
    async def get_all_links_metrics__all_rpc_requests_have_not_2xx_status_test(
            self, velocloud_repository, make_list_of_link_metrics, make_rpc_response, velocloud_500_response):
        velocloud_host_1 = "mettel.velocloud.net"
        velocloud_host_2 = "metvco02.mettel.net"
        velocloud_host_1_enterprise_1_id = 100
        velocloud_host_1_enterprise_2_id = 10000
        velocloud_host_2_enterprise_1_id = 1000000

        velo_filter_mock = {
            velocloud_host_1: [velocloud_host_1_enterprise_1_id, velocloud_host_2_enterprise_1_id],
            velocloud_host_2: [velocloud_host_1_enterprise_2_id]
        }

        interval = {
            'start': datetime.now() - timedelta(minutes=30),
            'end': datetime.now(),
        }

        links_metrics = make_list_of_link_metrics()
        response = make_rpc_response(
            request_id=uuid_,
            body=links_metrics,
            status=200,
        )

        velocloud_repository.get_links_metrics_by_host.return_value = velocloud_500_response

        custom_monitor_config = velocloud_repository._config.MONITOR_CONFIG.copy()
        custom_monitor_config['velo_filter'] = velo_filter_mock
        with patch.dict(velocloud_repository._config.MONITOR_CONFIG, custom_monitor_config):
            with uuid_mock:
                result = await velocloud_repository.get_all_links_metrics(interval)

        velocloud_repository.get_links_metrics_by_host.assert_any_await(host=velocloud_host_1, interval=interval)
        velocloud_repository.get_links_metrics_by_host.assert_any_await(host=velocloud_host_2, interval=interval)
        assert result == response

    @pytest.mark.asyncio
    async def get_all_links_metrics__all_rpc_requests_succeed_test(
            self, velocloud_repository, make_metrics_for_link, make_list_of_link_metrics, make_rpc_response):
        velocloud_host_1 = "mettel.velocloud.net"
        velocloud_host_2 = "metvco02.mettel.net"
        velocloud_host_1_enterprise_1_id = 100
        velocloud_host_1_enterprise_2_id = 10000
        velocloud_host_2_enterprise_1_id = 1000000

        velo_filter_mock = {
            velocloud_host_1: [velocloud_host_1_enterprise_1_id, velocloud_host_2_enterprise_1_id],
            velocloud_host_2: [velocloud_host_1_enterprise_2_id]
        }

        interval = {
            'start': datetime.now() - timedelta(minutes=30),
            'end': datetime.now(),
        }

        link_1_metrics = make_metrics_for_link(link_id=1)
        links_metrics_rpc_1 = make_list_of_link_metrics(link_1_metrics)
        rpc_1_response = make_rpc_response(
            request_id=uuid_,
            body=links_metrics_rpc_1,
            status=200,
        )

        link_2_metrics = make_metrics_for_link(link_id=2)
        links_metrics_rpc_2 = make_list_of_link_metrics(link_2_metrics)
        rpc_2_response = make_rpc_response(
            request_id=uuid_,
            body=links_metrics_rpc_2,
            status=200,
        )

        links_metrics = make_list_of_link_metrics(link_1_metrics, link_2_metrics)
        response = make_rpc_response(
            request_id=uuid_,
            body=links_metrics,
            status=200,
        )

        velocloud_repository.get_links_metrics_by_host.side_effect = [
            rpc_1_response,
            rpc_2_response,
        ]

        custom_monitor_config = velocloud_repository._config.MONITOR_CONFIG.copy()
        custom_monitor_config['velo_filter'] = velo_filter_mock
        with patch.dict(velocloud_repository._config.MONITOR_CONFIG, custom_monitor_config):
            with uuid_mock:
                result = await velocloud_repository.get_all_links_metrics(interval)

        velocloud_repository.get_links_metrics_by_host.assert_any_await(host=velocloud_host_1, interval=interval)
        velocloud_repository.get_links_metrics_by_host.assert_any_await(host=velocloud_host_2, interval=interval)
        assert result == response

    @pytest.mark.asyncio
    async def get_links_metrics_for_latency_checks_test(self, velocloud_repository, frozen_datetime):
        trouble = AffectingTroubles.LATENCY
        current_datetime = frozen_datetime.now()

        lookup_interval = velocloud_repository._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        interval = {
            'start': current_datetime - timedelta(minutes=lookup_interval),
            'end': current_datetime,
        }

        with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
            await velocloud_repository.get_links_metrics_for_latency_checks()

        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(interval=interval)

    @pytest.mark.asyncio
    async def get_links_metrics_for_packet_loss_checks_test(self, velocloud_repository, frozen_datetime):
        trouble = AffectingTroubles.PACKET_LOSS
        current_datetime = frozen_datetime.now()

        lookup_interval = velocloud_repository._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        interval = {
            'start': current_datetime - timedelta(minutes=lookup_interval),
            'end': current_datetime,
        }

        with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
            await velocloud_repository.get_links_metrics_for_packet_loss_checks()

        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(interval=interval)

    @pytest.mark.asyncio
    async def get_links_metrics_for_jitter_checks_test(self, velocloud_repository, frozen_datetime):
        trouble = AffectingTroubles.JITTER
        current_datetime = frozen_datetime.now()

        lookup_interval = velocloud_repository._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        interval = {
            'start': current_datetime - timedelta(minutes=lookup_interval),
            'end': current_datetime,
        }

        with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
            await velocloud_repository.get_links_metrics_for_jitter_checks()

        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(interval=interval)

    @pytest.mark.asyncio
    async def get_links_metrics_for_bandwidth_checks_test(self, velocloud_repository, frozen_datetime):
        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        current_datetime = frozen_datetime.now()

        lookup_interval = velocloud_repository._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        interval = {
            'start': current_datetime - timedelta(minutes=lookup_interval),
            'end': current_datetime,
        }

        with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
            await velocloud_repository.get_links_metrics_for_bandwidth_checks()

        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(interval=interval)

    @pytest.mark.asyncio
    async def get_links_metrics_for_autoresolve_test(self, velocloud_repository, frozen_datetime):
        current_datetime = frozen_datetime.now()

        lookup_interval = velocloud_repository._config.MONITOR_CONFIG['autoresolve']['metrics_lookup_interval_minutes']
        interval = {
            'start': current_datetime - timedelta(minutes=lookup_interval),
            'end': current_datetime,
        }

        with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
            await velocloud_repository.get_links_metrics_for_autoresolve()

        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(interval=interval)
