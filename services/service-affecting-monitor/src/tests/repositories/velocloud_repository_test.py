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
        velocloud_host_2 = "metvco03.mettel.net"
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
        velocloud_host_3 = "metvco03.mettel.net"
        velocloud_host_4 = "metvco04.mettel.net"
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

        link_3_metrics = make_metrics_for_link(link_id=3)
        links_metrics_rpc_3 = make_list_of_link_metrics(link_3_metrics)
        rpc_3_response = make_rpc_response(
            request_id=uuid_,
            body=links_metrics_rpc_3,
            status=200,
        )

        link_4_metrics = make_metrics_for_link(link_id=4)
        links_metrics_rpc_4 = make_list_of_link_metrics(link_4_metrics)
        rpc_4_response = make_rpc_response(
            request_id=uuid_,
            body=links_metrics_rpc_4,
            status=200,
        )

        links_metrics = make_list_of_link_metrics(link_1_metrics, link_2_metrics, link_3_metrics, link_4_metrics)
        response = make_rpc_response(
            request_id=uuid_,
            body=links_metrics,
            status=200,
        )

        velocloud_repository.get_links_metrics_by_host.side_effect = [
            rpc_1_response,
            rpc_2_response,
            rpc_3_response,
            rpc_4_response,
        ]

        custom_monitor_config = velocloud_repository._config.MONITOR_CONFIG.copy()
        custom_monitor_config['velo_filter'] = velo_filter_mock
        with patch.dict(velocloud_repository._config.MONITOR_CONFIG, custom_monitor_config):
            with uuid_mock:
                result = await velocloud_repository.get_all_links_metrics(interval)

        velocloud_repository.get_links_metrics_by_host.assert_any_await(host=velocloud_host_1, interval=interval)
        velocloud_repository.get_links_metrics_by_host.assert_any_await(host=velocloud_host_2, interval=interval)
        velocloud_repository.get_links_metrics_by_host.assert_any_await(host=velocloud_host_3, interval=interval)
        velocloud_repository.get_links_metrics_by_host.assert_any_await(host=velocloud_host_4, interval=interval)
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
    async def get_links_metrics_for_bouncing_checks_test(self, velocloud_repository, frozen_datetime):
        trouble = AffectingTroubles.BOUNCING
        current_datetime = frozen_datetime.now()

        lookup_interval = velocloud_repository._config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][trouble]
        interval = {
            'start': current_datetime - timedelta(minutes=lookup_interval),
            'end': current_datetime,
        }

        with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
            await velocloud_repository.get_links_metrics_for_bouncing_checks()

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

    @pytest.mark.asyncio
    async def get_links_metrics_for_bandwidth_reports_test(self, velocloud_repository, frozen_datetime):
        current_datetime = frozen_datetime.now()

        lookup_interval = velocloud_repository._config.BANDWIDTH_REPORT_CONFIG['lookup_interval_hours']
        interval = {
            'start': current_datetime - timedelta(hours=lookup_interval),
            'end': current_datetime,
        }

        with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
            await velocloud_repository.get_links_metrics_for_bandwidth_reports()

        velocloud_repository.get_all_links_metrics.assert_awaited_once_with(interval=interval)

    @pytest.mark.asyncio
    async def get_enterprise_events__events_retrieved_test(self, velocloud_repository, frozen_datetime,
                                                           make_get_enterprise_events_request, make_rpc_response):
        host = 'mettel.velocloud.net'
        enterprise_id = 1
        event_types = ['LINK_DEAD']
        events = []

        config = velocloud_repository._config
        now = frozen_datetime.now()
        minutes = config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][AffectingTroubles.BOUNCING]
        past_moment = now - timedelta(minutes=minutes)

        request = make_get_enterprise_events_request(
            request_id=uuid_,
            host=host,
            enterprise_id=enterprise_id,
            start_date=past_moment,
            end_date=now,
            filter_=event_types,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body=events,
            status=200,
        )

        velocloud_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
                result = await velocloud_repository.get_enterprise_events(host, enterprise_id)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "alert.request.event.enterprise", request, timeout=180
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_enterprise_events__rpc_request_failing_test(self, velocloud_repository, frozen_datetime,
                                                              make_get_enterprise_events_request):
        host = 'mettel.velocloud.net'
        enterprise_id = 1
        event_types = ['LINK_DEAD']

        now = frozen_datetime.now()
        config = velocloud_repository._config
        minutes = config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][AffectingTroubles.BOUNCING]
        past_moment = now - timedelta(minutes=minutes)

        request = make_get_enterprise_events_request(
            request_id=uuid_,
            host=host,
            enterprise_id=enterprise_id,
            start_date=past_moment,
            end_date=now,
            filter_=event_types,
        )

        velocloud_repository._event_bus.rpc_request.side_effect = Exception
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
                result = await velocloud_repository.get_enterprise_events(host, enterprise_id)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "alert.request.event.enterprise", request, timeout=180
        )
        velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        velocloud_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_enterprise_events__rpc_request_has_not_2xx_status_test(self, velocloud_repository, frozen_datetime,
                                                                         make_get_enterprise_events_request,
                                                                         velocloud_500_response):
        host = 'mettel.velocloud.net'
        enterprise_id = 1
        event_types = ['LINK_DEAD']

        now = frozen_datetime.now()
        config = velocloud_repository._config
        minutes = config.MONITOR_CONFIG['monitoring_minutes_per_trouble'][AffectingTroubles.BOUNCING]
        past_moment = now - timedelta(minutes=minutes)

        request = make_get_enterprise_events_request(
            request_id=uuid_,
            host=host,
            enterprise_id=enterprise_id,
            start_date=past_moment,
            end_date=now,
            filter_=event_types,
        )

        velocloud_repository._event_bus.rpc_request.return_value = velocloud_500_response
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            with patch.object(velocloud_repository_module, 'datetime', new=frozen_datetime):
                result = await velocloud_repository.get_enterprise_events(host, enterprise_id)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "alert.request.event.enterprise", request, timeout=180
        )
        velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        velocloud_repository._logger.error.assert_called_once()
        assert result == velocloud_500_response

    @pytest.mark.asyncio
    async def get_events_by_serial_and_interface__all_rpc_requests_have_not_2xx_status_test(self, velocloud_repository,
                                                                                            make_edge_full_id,
                                                                                            make_cached_edge,
                                                                                            make_customer_cache,
                                                                                            velocloud_500_response):
        host_1 = 'mettel.velocloud.net'
        host_2 = 'metvco03.mettel.net'

        enterprise_id_1 = 1
        enterprise_id_2 = 2

        edge_1_full_id = make_edge_full_id(host=host_1, enterprise_id=enterprise_id_1)
        edge_2_full_id = make_edge_full_id(host=host_1, enterprise_id=enterprise_id_2)
        edge_3_full_id = make_edge_full_id(host=host_2, enterprise_id=enterprise_id_1)

        edge_1 = make_cached_edge(full_id=edge_1_full_id)
        edge_2 = make_cached_edge(full_id=edge_2_full_id)
        edge_3 = make_cached_edge(full_id=edge_3_full_id)

        customer_cache = make_customer_cache(edge_1, edge_2, edge_3)

        velocloud_repository.get_enterprise_events.return_value = velocloud_500_response

        with uuid_mock:
            result = await velocloud_repository.get_events_by_serial_and_interface(customer_cache)

        velocloud_repository.get_enterprise_events.assert_any_await(host_1, enterprise_id_1)
        velocloud_repository.get_enterprise_events.assert_any_await(host_1, enterprise_id_2)
        velocloud_repository.get_enterprise_events.assert_any_await(host_2, enterprise_id_1)

        expected = {}

        assert result == expected

    @pytest.mark.asyncio
    async def get_events_by_serial_and_interface__all_rpc_requests_succeed_test(self, velocloud_repository, make_event,
                                                                                make_edge_full_id, make_cached_edge,
                                                                                make_customer_cache, make_rpc_response):
        edge_name_1 = 'Edge 1'
        edge_name_2 = 'Edge 2'

        event_1 = make_event(edge_name=edge_name_1, message='Link GE1 is now DEAD')
        event_2 = make_event(edge_name=edge_name_2)

        host_1 = 'mettel.velocloud.net'
        host_2 = 'metvco03.mettel.net'

        enterprise_id_1 = 1
        enterprise_id_2 = 2

        edge_1_full_id = make_edge_full_id(host=host_1, enterprise_id=enterprise_id_1)
        edge_2_full_id = make_edge_full_id(host=host_1, enterprise_id=enterprise_id_2)
        edge_3_full_id = make_edge_full_id(host=host_2, enterprise_id=enterprise_id_1)

        edge_1_serial = 'VC1111111'
        edge_2_serial = 'VC2222222'
        edge_3_serial = 'VC3333333'

        edge_1 = make_cached_edge(full_id=edge_1_full_id, serial_number=edge_1_serial, name=edge_name_1)
        edge_2 = make_cached_edge(full_id=edge_2_full_id, serial_number=edge_2_serial)
        edge_3 = make_cached_edge(full_id=edge_3_full_id, serial_number=edge_3_serial)

        customer_cache = make_customer_cache(edge_1, edge_2, edge_3)

        rpc_1_response = make_rpc_response(request_id=uuid_, status=200, body=[event_1])
        rpc_2_response = make_rpc_response(request_id=uuid_, status=200, body=[event_2])
        rpc_3_response = make_rpc_response(request_id=uuid_, status=200, body=[])

        velocloud_repository.get_enterprise_events.side_effect = [
            rpc_1_response,
            rpc_2_response,
            rpc_3_response,
        ]

        with uuid_mock:
            result = await velocloud_repository.get_events_by_serial_and_interface(customer_cache)

        velocloud_repository.get_enterprise_events.assert_any_await(host_1, enterprise_id_1)
        velocloud_repository.get_enterprise_events.assert_any_await(host_1, enterprise_id_2)
        velocloud_repository.get_enterprise_events.assert_any_await(host_2, enterprise_id_1)

        expected = {
            edge_1_serial: {
                'GE1': [event_1]
            },
        }

        assert result == expected

    def structure_edges_by_host_and_enterprise_test(self, velocloud_repository, make_edge_full_id, make_cached_edge,
                                                    make_customer_cache):
        edge_1_full_id = make_edge_full_id(host='mettel.velocloud.net', enterprise_id=1)
        edge_2_full_id = make_edge_full_id(host='mettel.velocloud.net', enterprise_id=2)
        edge_3_full_id = make_edge_full_id(host='metvco03.mettel.net', enterprise_id=1)
        edge_4_full_id = make_edge_full_id(host='metvco03.mettel.net', enterprise_id=1)

        edge_1 = make_cached_edge(full_id=edge_1_full_id)
        edge_2 = make_cached_edge(full_id=edge_2_full_id)
        edge_3 = make_cached_edge(full_id=edge_3_full_id)
        edge_4 = make_cached_edge(full_id=edge_4_full_id)

        customer_cache = make_customer_cache(edge_1, edge_2, edge_3, edge_4)
        result = velocloud_repository._structure_edges_by_host_and_enterprise(customer_cache)

        expected = {
            'mettel.velocloud.net': {
                1: [edge_1],
                2: [edge_2],
            },
            'metvco03.mettel.net': {
                1: [edge_3, edge_4],
            },
        }

        assert result == expected

    def filter_links_metrics_by_client_test(self, velocloud_repository, make_edge, make_metrics_for_link,
                                            make_edge_full_id, make_bruin_client_info, make_cached_edge,
                                            make_customer_cache):
        host = 'mettel.velocloud.net'
        enterprise_id = 123
        edge_id = 456
        client_id = 789

        edge = make_edge(host=host, enterprise_id=enterprise_id, id_=edge_id)
        link_1_metrics = make_metrics_for_link(link_with_edge_info=edge)
        link_2_metrics = make_metrics_for_link()
        links_metrics = [link_1_metrics, link_2_metrics]

        edge_full_id = make_edge_full_id(host=host, enterprise_id=enterprise_id, edge_id=edge_id)
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        cached_edge = make_cached_edge(full_id=edge_full_id, bruin_client_info=bruin_client_info)
        customer_cache = make_customer_cache(cached_edge)

        result = velocloud_repository.filter_links_metrics_by_client(links_metrics, client_id, customer_cache)
        expected = [link_1_metrics]
        assert result == expected
