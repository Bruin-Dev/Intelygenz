from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from shortuuid import uuid

from application import AffectingTroubles
from application.actions import service_affecting_monitor as service_affecting_monitor_module
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(service_affecting_monitor_module, 'uuid', return_value=uuid_)


class TestServiceAffectingMonitor:

    def instance_test(self, service_affecting_monitor, logger, scheduler, customer_cache_repository, bruin_repository,
                      velocloud_repository, notifications_repository, ticket_repository, trouble_repository,
                      metrics_repository, utils_repository):
        assert service_affecting_monitor._logger is logger
        assert service_affecting_monitor._scheduler is scheduler
        assert service_affecting_monitor._config is testconfig
        assert service_affecting_monitor._customer_cache_repository is customer_cache_repository
        assert service_affecting_monitor._bruin_repository is bruin_repository
        assert service_affecting_monitor._velocloud_repository is velocloud_repository
        assert service_affecting_monitor._notifications_repository is notifications_repository
        assert service_affecting_monitor._ticket_repository is ticket_repository
        assert service_affecting_monitor._trouble_repository is trouble_repository
        assert service_affecting_monitor._metrics_repository is metrics_repository
        assert service_affecting_monitor._utils_repository is utils_repository

        assert service_affecting_monitor._customer_cache == []

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job__exec_on_start_test(self, service_affecting_monitor, frozen_datetime):
        next_run_time = frozen_datetime.now()
        with patch.multiple(service_affecting_monitor_module, datetime=frozen_datetime, timezone=Mock()):
            await service_affecting_monitor.start_service_affecting_monitor(exec_on_start=True)

        service_affecting_monitor._scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._service_affecting_monitor_process, 'interval',
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_service_affecting_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job__no_exec_on_start_test(self, service_affecting_monitor):
        await service_affecting_monitor.start_service_affecting_monitor(exec_on_start=False)

        service_affecting_monitor._scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._service_affecting_monitor_process, 'interval',
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=undefined,
            replace_existing=False,
            id='_service_affecting_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job__job_already_executing_test(self, service_affecting_monitor):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        service_affecting_monitor._scheduler.add_job = Mock(side_effect=exception_instance)
        await service_affecting_monitor.start_service_affecting_monitor()
        service_affecting_monitor._logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def service_affecting_monitor_process__get_cache_request_has_202_status_test(
            self, service_affecting_monitor, get_customer_cache_202_response):
        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = \
            get_customer_cache_202_response

        await service_affecting_monitor._service_affecting_monitor_process()

        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_not_awaited()
        service_affecting_monitor._packet_loss_check.assert_not_awaited()
        service_affecting_monitor._jitter_check.assert_not_awaited()
        service_affecting_monitor._bandwidth_check.assert_not_awaited()
        service_affecting_monitor._run_autoresolve_process.assert_not_awaited()
        assert service_affecting_monitor._customer_cache == []

    @pytest.mark.asyncio
    async def service_affecting_monitor_process__get_cache_request_has_2xx_status_different_from_202_test(
            self, service_affecting_monitor, get_customer_cache_404_response):
        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = \
            get_customer_cache_404_response

        await service_affecting_monitor._service_affecting_monitor_process()

        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_not_awaited()
        service_affecting_monitor._packet_loss_check.assert_not_awaited()
        service_affecting_monitor._jitter_check.assert_not_awaited()
        service_affecting_monitor._bandwidth_check.assert_not_awaited()
        service_affecting_monitor._run_autoresolve_process.assert_not_awaited()
        assert service_affecting_monitor._customer_cache == []

    @pytest.mark.asyncio
    async def service_affecting_monitor_process__get_cache_request_returns_empty_list_of_edges_test(
            self, service_affecting_monitor, get_customer_cache_empty_response):
        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = \
            get_customer_cache_empty_response

        await service_affecting_monitor._service_affecting_monitor_process()

        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_not_awaited()
        service_affecting_monitor._packet_loss_check.assert_not_awaited()
        service_affecting_monitor._jitter_check.assert_not_awaited()
        service_affecting_monitor._bandwidth_check.assert_not_awaited()
        service_affecting_monitor._run_autoresolve_process.assert_not_awaited()
        assert service_affecting_monitor._customer_cache == []

    @pytest.mark.asyncio
    async def service_affecting_monitor_process__ok_test(self, service_affecting_monitor, make_customer_cache,
                                                         make_cached_edge, make_rpc_response):
        edge_1 = make_cached_edge()
        edge_2 = make_cached_edge()
        customer_cache = make_customer_cache(edge_1, edge_2)

        get_cache_response = make_rpc_response(
            body=customer_cache,
            status=200,
        )

        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = \
            get_cache_response

        await service_affecting_monitor._service_affecting_monitor_process()

        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_awaited_once()
        service_affecting_monitor._packet_loss_check.assert_awaited_once()
        service_affecting_monitor._jitter_check.assert_awaited_once()
        service_affecting_monitor._bandwidth_check.assert_awaited_once()
        service_affecting_monitor._run_autoresolve_process.assert_awaited_once()
        assert service_affecting_monitor._customer_cache == customer_cache

    def structure_links_metrics__ok_test(self, service_affecting_monitor, make_edge, make_link, make_metrics,
                                         make_link_with_edge_info, make_link_with_metrics, make_metrics_for_link,
                                         make_list_of_links_with_metrics, make_structured_metrics_object,
                                         make_list_of_structured_metrics_objects):
        edge_id = 1
        link_1_id = 1
        link_2_id = 2

        metric_set_1 = make_metrics()
        metric_set_2 = make_metrics()

        edge = make_edge(id_=edge_id)
        link_1 = make_link(id_=link_1_id)
        link_2 = make_link(id_=link_2_id)
        metric_set_1_with_link_1_info = make_metrics_for_link(link_id=link_1, metrics=metric_set_1)
        metric_set_2_with_link_2_info = make_metrics_for_link(link_id=link_2, metrics=metric_set_2)

        link_1_with_edge_info = make_link_with_edge_info(link_info=link_1, edge_info=edge)
        link_2_with_edge_info = make_link_with_edge_info(link_info=link_2, edge_info=edge)
        link_1_info_with_metrics = make_link_with_metrics(
            link_info=link_1_with_edge_info, metrics=metric_set_1_with_link_1_info,
        )
        link_2_info_with_metrics = make_link_with_metrics(
            link_info=link_2_with_edge_info, metrics=metric_set_2_with_link_2_info,
        )
        links_info_with_metrics = make_list_of_links_with_metrics(link_1_info_with_metrics, link_2_info_with_metrics)

        result = service_affecting_monitor._structure_links_metrics(links_info_with_metrics)

        structured_metrics_1 = make_structured_metrics_object(edge_info=edge, link_info=link_1, metrics=metric_set_1)
        structured_metrics_2 = make_structured_metrics_object(edge_info=edge, link_info=link_2, metrics=metric_set_2)
        expected = make_list_of_structured_metrics_objects(structured_metrics_1, structured_metrics_2)
        assert result == expected

    def structure_links_metrics__bad_edge_id_test(self, service_affecting_monitor, make_edge, make_link,
                                                  make_metrics, make_link_with_edge_info, make_link_with_metrics,
                                                  make_metrics_for_link, make_list_of_links_with_metrics):
        edge_id = 0
        link_1_id = 1
        link_2_id = 2

        metric_set_1 = make_metrics()
        metric_set_2 = make_metrics()

        edge = make_edge(id_=edge_id)
        link_1 = make_link(id_=link_1_id)
        link_2 = make_link(id_=link_2_id)
        metric_set_1_with_link_1_info = make_metrics_for_link(link_id=link_1, metrics=metric_set_1)
        metric_set_2_with_link_2_info = make_metrics_for_link(link_id=link_2, metrics=metric_set_2)

        link_1_with_edge_info = make_link_with_edge_info(link_info=link_1, edge_info=edge)
        link_2_with_edge_info = make_link_with_edge_info(link_info=link_2, edge_info=edge)
        link_1_info_with_metrics = make_link_with_metrics(
            link_info=link_1_with_edge_info, metrics=metric_set_1_with_link_1_info,
        )
        link_2_info_with_metrics = make_link_with_metrics(
            link_info=link_2_with_edge_info, metrics=metric_set_2_with_link_2_info,
        )
        links_info_with_metrics = make_list_of_links_with_metrics(link_1_info_with_metrics, link_2_info_with_metrics)

        result = service_affecting_monitor._structure_links_metrics(links_info_with_metrics)

        expected = []
        assert result == expected

    def map_cached_edges_with_links_metrics_and_contact_info__no_edges_in_contact_info_test(
            self, service_affecting_monitor, make_edge, make_link, make_metrics,
            make_structured_metrics_object, make_list_of_structured_metrics_objects):
        edge = make_edge()
        link_1 = make_link()
        link_2 = make_link()

        link_1_metric_set = make_metrics()
        link_2_metric_set = make_metrics()

        structured_metrics_1 = make_structured_metrics_object(
            edge_info=edge, link_info=link_1, metrics=link_1_metric_set,
        )
        structured_metrics_2 = make_structured_metrics_object(
            edge_info=edge, link_info=link_2, metrics=link_2_metric_set,
        )
        structured_metrics = make_list_of_structured_metrics_objects(structured_metrics_1, structured_metrics_2)

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['devices_by_id'] = []

        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            result = service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info(structured_metrics)

        expected = []
        assert result == expected

    def map_cached_edges_with_links_metrics_and_contact_info__edge_in_cache_and_in_contact_info_but_not_in_metrics_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache, make_edge,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_list_of_structured_metrics_objects_with_cache_and_contact_info,
    ):
        # Let's just pick a couple of edges from the contact_info object to use them as a reference
        edge_1_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]
        edge_2_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][1]

        edge_1_serial_number = edge_1_contact_info['serial']
        edge_2_serial_number = edge_2_contact_info['serial']

        edge_1_cache_info = make_cached_edge(serial_number=edge_1_serial_number)
        edge_2_cache_info = make_cached_edge(serial_number=edge_2_serial_number)

        edge_2 = make_edge(serial_number=edge_2_serial_number)
        edge_2_structured_metrics = make_structured_metrics_object(edge_info=edge_2)
        structured_metrics = make_list_of_structured_metrics_objects(edge_2_structured_metrics)

        customer_cache = make_customer_cache(edge_1_cache_info, edge_2_cache_info)
        service_affecting_monitor._customer_cache = customer_cache

        result = service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info(structured_metrics)

        edge_2_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=edge_2_structured_metrics,
            cache_info=edge_2_cache_info,
            contact_info=edge_2_contact_info['contacts'],
        )
        expected = make_list_of_structured_metrics_objects_with_cache_and_contact_info(edge_2_complete_info)
        assert result == expected

    def map_cached_edges_with_links_metrics_and_contact_info__edge_in_metrics_and_in_contact_info_but_not_in_cache_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache, make_edge,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_list_of_structured_metrics_objects_with_cache_and_contact_info,
    ):
        # Let's just pick a couple of edges from the contact_info object to use them as a reference
        edge_1_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]
        edge_2_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][1]

        edge_1_serial_number = edge_1_contact_info['serial']
        edge_2_serial_number = edge_2_contact_info['serial']

        edge_1_cache_info = make_cached_edge(serial_number=edge_1_serial_number)

        edge_1 = make_edge(serial_number=edge_1_serial_number)
        edge_2 = make_edge(serial_number=edge_2_serial_number)
        edge_1_structured_metrics = make_structured_metrics_object(edge_info=edge_1)
        edge_2_structured_metrics = make_structured_metrics_object(edge_info=edge_2)
        structured_metrics = make_list_of_structured_metrics_objects(
            edge_1_structured_metrics, edge_2_structured_metrics,
        )

        customer_cache = make_customer_cache(edge_1_cache_info)
        service_affecting_monitor._customer_cache = customer_cache

        result = service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info(structured_metrics)

        edge_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=edge_1_structured_metrics,
            cache_info=edge_1_cache_info,
            contact_info=edge_1_contact_info['contacts'],
        )
        expected = make_list_of_structured_metrics_objects_with_cache_and_contact_info(edge_1_complete_info)
        assert result == expected

    def map_cached_edges_with_links_metrics_and_contact_info__edge_in_metrics_and_in_contact_info_and_in_cache_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache, make_edge,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_list_of_structured_metrics_objects_with_cache_and_contact_info,
    ):
        # Let's just pick a couple of edges from the contact_info object to use them as a reference
        edge_1_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]
        edge_2_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][1]

        edge_1_serial_number = edge_1_contact_info['serial']
        edge_2_serial_number = edge_2_contact_info['serial']

        edge_1_cache_info = make_cached_edge(serial_number=edge_1_serial_number)
        edge_2_cache_info = make_cached_edge(serial_number=edge_2_serial_number)

        edge_1 = make_edge(serial_number=edge_1_serial_number)
        edge_2 = make_edge(serial_number=edge_2_serial_number)
        edge_1_structured_metrics = make_structured_metrics_object(edge_info=edge_1)
        edge_2_structured_metrics = make_structured_metrics_object(edge_info=edge_2)
        structured_metrics = make_list_of_structured_metrics_objects(
            edge_1_structured_metrics, edge_2_structured_metrics,
        )

        customer_cache = make_customer_cache(edge_1_cache_info, edge_2_cache_info)
        service_affecting_monitor._customer_cache = customer_cache

        result = service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info(structured_metrics)

        edge_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=edge_1_structured_metrics,
            cache_info=edge_1_cache_info,
            contact_info=edge_1_contact_info['contacts'],
        )
        edge_2_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=edge_2_structured_metrics,
            cache_info=edge_2_cache_info,
            contact_info=edge_2_contact_info['contacts'],
        )
        expected = make_list_of_structured_metrics_objects_with_cache_and_contact_info(
            edge_1_complete_info, edge_2_complete_info,
        )
        assert result == expected

    @pytest.mark.asyncio
    async def latency_check__no_metrics_found_test(self, service_affecting_monitor, make_list_of_link_metrics,
                                                   make_rpc_response):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_latency_checks.return_value = \
            make_rpc_response(
                body=links_metrics,
                status=200,
            )

        await service_affecting_monitor._latency_check()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_latency_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check__empty_dataset_after_structuring_and_crossing_info_test(
            self, service_affecting_monitor, make_edge, make_link_with_edge_info, make_metrics_for_link,
            make_list_of_link_metrics, make_list_of_structured_metrics_objects_with_cache_and_contact_info,
            make_rpc_response):
        edge = make_edge(id_=0)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_latency_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._latency_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_complete_info,
        )
        service_affecting_monitor._process_latency_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check__all_metrics_within_thresholds_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache,
            make_edge, make_metrics, make_link_with_edge_info, make_metrics_for_link, make_list_of_link_metrics,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_latency_ms_tx=0, best_latency_ms_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_latency_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._latency_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_latency_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check__trouble_detected_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache,
            make_edge, make_metrics, make_link_with_edge_info, make_metrics_for_link, make_list_of_link_metrics,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_latency_ms_tx=9999, best_latency_ms_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_latency_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._latency_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_latency_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def packet_loss_check__no_metrics_found_test(self, service_affecting_monitor, make_list_of_link_metrics,
                                                       make_rpc_response):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_packet_loss_checks.return_value = \
            make_rpc_response(
                body=links_metrics,
                status=200,
            )

        await service_affecting_monitor._packet_loss_check()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_packet_loss_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check__empty_dataset_after_structuring_and_crossing_info_test(
            self, service_affecting_monitor, make_edge, make_link_with_edge_info, make_metrics_for_link,
            make_list_of_link_metrics, make_list_of_structured_metrics_objects_with_cache_and_contact_info,
            make_rpc_response):
        edge = make_edge(id_=0)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_packet_loss_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._packet_loss_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_complete_info,
        )
        service_affecting_monitor._process_packet_loss_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check__all_metrics_within_thresholds_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache,
            make_edge, make_metrics, make_link_with_edge_info, make_metrics_for_link, make_list_of_link_metrics,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_packet_loss_tx=0, best_packet_loss_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_packet_loss_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._packet_loss_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_packet_loss_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check__trouble_detected_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache,
            make_edge, make_metrics, make_link_with_edge_info, make_metrics_for_link, make_list_of_link_metrics,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_packet_loss_tx=9999, best_packet_loss_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_packet_loss_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._packet_loss_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_packet_loss_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def jitter_check__no_metrics_found_test(self, service_affecting_monitor, make_list_of_link_metrics,
                                                  make_rpc_response):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_jitter_checks.return_value = \
            make_rpc_response(
                body=links_metrics,
                status=200,
            )

        await service_affecting_monitor._jitter_check()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_jitter_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def jitter_check__empty_dataset_after_structuring_and_crossing_info_test(
            self, service_affecting_monitor, make_edge, make_link_with_edge_info, make_metrics_for_link,
            make_list_of_link_metrics, make_list_of_structured_metrics_objects_with_cache_and_contact_info,
            make_rpc_response):
        edge = make_edge(id_=0)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_jitter_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._jitter_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_complete_info,
        )
        service_affecting_monitor._process_jitter_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def jitter_check__all_metrics_within_thresholds_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache,
            make_edge, make_metrics, make_link_with_edge_info, make_metrics_for_link, make_list_of_link_metrics,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_jitter_ms_tx=0, best_jitter_ms_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_jitter_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._jitter_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_jitter_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def jitter_check__trouble_detected_test(
            self, service_affecting_monitor, make_cached_edge, make_customer_cache,
            make_edge, make_metrics, make_link_with_edge_info, make_metrics_for_link, make_list_of_link_metrics,
            make_structured_metrics_object, make_list_of_structured_metrics_objects,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_jitter_ms_tx=9999, best_jitter_ms_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_jitter_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._jitter_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_jitter_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def bandwidth_check__no_metrics_found_test(self, service_affecting_monitor, make_list_of_link_metrics,
                                                     make_rpc_response):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = \
            make_rpc_response(
                body=links_metrics,
                status=200,
            )

        await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__empty_dataset_after_structuring_and_crossing_info_test(
            self, service_affecting_monitor, make_edge, make_link_with_edge_info, make_metrics_for_link,
            make_list_of_link_metrics, make_list_of_structured_metrics_objects, make_rpc_response):
        edge = make_edge(id_=0)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_structured_metrics = make_list_of_structured_metrics_objects()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_structured_metrics,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__unmonitorized_bruin_clients_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_customer_cache, make_edge, make_metrics, make_link_with_edge_info,
            make_metrics_for_link, make_list_of_link_metrics, make_structured_metrics_object,
            make_list_of_structured_metrics_objects, make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        edge_link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_metrics = make_metrics()
        edge_link_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_with_edge_info, metrics=edge_link_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=edge_link_metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_bruin_client_info = make_bruin_client_info(client_id=30000)  # MetTel's client ID in Bruin
        edge_cache_info = make_cached_edge(serial_number=edge_serial_number, bruin_client_info=edge_bruin_client_info)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__invalid_tx_and_rx_bandwidth_metrics_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_customer_cache, make_edge, make_metrics, make_link_with_edge_info,
            make_metrics_for_link, make_list_of_link_metrics, make_structured_metrics_object,
            make_list_of_structured_metrics_objects, make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        edge_link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_metrics = make_metrics(bps_of_best_path_tx=0, bps_of_best_path_rx=0)
        edge_link_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_with_edge_info, metrics=edge_link_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=edge_link_metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_bruin_client_info = make_bruin_client_info(client_id=83109)  # RSI's client ID in Bruin
        edge_cache_info = make_cached_edge(serial_number=edge_serial_number, bruin_client_info=edge_bruin_client_info)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__all_metrics_within_thresholds_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_customer_cache, make_edge, make_metrics, make_link_with_edge_info,
            make_metrics_for_link, make_list_of_link_metrics, make_structured_metrics_object,
            make_list_of_structured_metrics_objects, make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][1]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        edge_link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_metrics = make_metrics(bps_of_best_path_tx=100, bps_of_best_path_rx=100)
        edge_link_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_with_edge_info, metrics=edge_link_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_metric_set)

        structured_metrics_object = make_structured_metrics_object(
            edge_info=edge, metrics=edge_link_metrics,
        )
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_bruin_client_info = make_bruin_client_info(client_id=83109)  # RSI's client ID in Bruin
        edge_cache_info = make_cached_edge(serial_number=edge_serial_number, bruin_client_info=edge_bruin_client_info)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__trouble_detected_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_customer_cache, make_edge, make_metrics, make_link_with_edge_info,
            make_metrics_for_link, make_list_of_link_metrics, make_structured_metrics_object,
            make_list_of_structured_metrics_objects, make_structured_metrics_object_with_cache_and_contact_info,
            make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][1]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        edge_link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_metrics = make_metrics(
            bytes_tx=999999, bytes_rx=999999,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        edge_link_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_with_edge_info, metrics=edge_link_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_metric_set)

        structured_metrics_object = make_structured_metrics_object(
            edge_info=edge, metrics=edge_link_metrics,
        )
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_bruin_client_info = make_bruin_client_info(client_id=83109)  # RSI's client ID in Bruin
        edge_cache_info = make_cached_edge(serial_number=edge_serial_number, bruin_client_info=edge_bruin_client_info)
        customer_cache = make_customer_cache(edge_cache_info)

        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def process_latency_trouble_test(
            self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.LATENCY
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_latency_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)

    @pytest.mark.asyncio
    async def process_jitter_trouble_test(
            self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.JITTER
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_jitter_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)

    @pytest.mark.asyncio
    async def process_packet_loss_trouble_test(
            self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.PACKET_LOSS
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_packet_loss_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)

    @pytest.mark.asyncio
    async def process_bandwidth_trouble_test(
            self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_bandwidth_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)

    @pytest.mark.asyncio
    async def process_affecting_trouble__get_open_affecting_tickets_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_bruin_client_info, make_cached_edge,
            make_structured_metrics_object_with_cache_and_contact_info,
            bruin_500_response):
        service_number = 'VC1234567'
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = bruin_500_response

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__open_ticket_found_with_resolved_detail_for_serial_test(
            self, service_affecting_monitor, make_bruin_client_info, make_cached_edge,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_ticket, make_list_of_tickets, make_detail_item, make_detail_item_with_notes_and_ticket_info,
            make_rpc_response):
        service_number = 'VC1234567'
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        ticket = make_ticket()
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(status='R')  # Resolved
        detail_object = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, ticket_info=ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = detail_object

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_awaited_once_with(
            detail_object, trouble, link_info,
        )
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__open_ticket_found_with_in_progress_detail_for_serial_test(
            self, service_affecting_monitor, make_bruin_client_info, make_cached_edge,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_ticket, make_list_of_tickets, make_detail_item, make_detail_item_with_notes_and_ticket_info,
            make_rpc_response):
        service_number = 'VC1234567'
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        ticket = make_ticket()
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(status='I')  # In progress
        detail_object = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, ticket_info=ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = detail_object

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_awaited_once_with(
            detail_object, trouble, link_info,
        )
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__get_resolved_affecting_tickets_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_bruin_client_info, make_cached_edge,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_ticket, make_list_of_tickets, make_detail_item, make_detail_item_with_notes_and_ticket_info,
            make_rpc_response, bruin_500_response):
        service_number = 'VC1234567'
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        ticket = make_ticket()
        open_affecting_tickets = make_list_of_tickets()

        detail_item = make_detail_item()
        detail_object = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, ticket_info=ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.return_value = bruin_500_response
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = \
            None  # No Open ticket was found

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__resolved_ticket_found_test(
            self, service_affecting_monitor, make_bruin_client_info, make_cached_edge,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_ticket, make_list_of_tickets, make_detail_item, make_detail_item_with_notes_and_ticket_info,
            make_rpc_response):
        service_number = 'VC1234567'
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        ticket = make_ticket()
        open_affecting_tickets = make_list_of_tickets()
        resolved_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item()
        detail_object = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, ticket_info=ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.return_value = make_rpc_response(
            body=resolved_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.side_effect = [
            None,           # No Open ticket was found
            detail_object,  # Resolved ticket was found
        ]

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_awaited_once_with(
            detail_object, trouble, link_info,
        )
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__no_open_or_resolved_ticket_found_test(
            self, service_affecting_monitor, make_bruin_client_info, make_cached_edge,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_list_of_tickets, make_rpc_response):
        service_number = 'VC1234567'
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        open_affecting_tickets = make_list_of_tickets()
        resolved_affecting_tickets = make_list_of_tickets()

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.return_value = make_rpc_response(
            body=resolved_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = \
            None  # No Open or Resolved tickets found

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=service_number,
        )
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_awaited_once_with(trouble, link_info)

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__empty_list_of_tickets_test(
            self, service_affecting_monitor, make_ticket, make_list_of_tickets, bruin_500_response):
        service_number = 'VC1234567'

        tickets = make_list_of_tickets()

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = bruin_500_response

        result = await service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number(
            tickets, service_number,
        )
        assert result is None

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__get_details_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_ticket, make_list_of_tickets, bruin_500_response):
        service_number = 'VC1234567'

        ticket = make_ticket()
        tickets = make_list_of_tickets(ticket)

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = bruin_500_response

        result = await service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number(
            tickets, service_number,
        )
        assert result is None

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__no_notes_found_for_serial_number_test(
            self, service_affecting_monitor, make_ticket, make_list_of_tickets, make_detail_item,
            make_list_of_detail_items, make_ticket_note, make_list_of_ticket_notes, make_ticket_details,
            make_detail_item_with_notes_and_ticket_info, make_rpc_response):
        service_number = 'VC1234567'
        fake_service_number = 'VC0000000'

        ticket = make_ticket()
        tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=service_number)
        detail_items = make_list_of_detail_items(detail_item)

        note_1 = make_ticket_note(service_numbers=[fake_service_number])
        note_2 = make_ticket_note(service_numbers=[fake_service_number])
        ticket_notes = make_list_of_ticket_notes(note_1, note_2)

        ticket_details = make_ticket_details(detail_items=detail_items, notes=ticket_notes)

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        result = await service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number(
            tickets, service_number,
        )

        expected_notes = make_list_of_ticket_notes()
        expected = make_detail_item_with_notes_and_ticket_info(
            detail_item=detail_item, notes=expected_notes, ticket_info=ticket,
        )
        assert result == expected

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__invalid_notes_found_for_serial_number_test(
            self, service_affecting_monitor, make_ticket, make_list_of_tickets, make_detail_item,
            make_list_of_detail_items, make_ticket_note, make_list_of_ticket_notes, make_ticket_details,
            make_detail_item_with_notes_and_ticket_info, make_rpc_response):
        service_number = 'VC1234567'

        ticket = make_ticket()
        tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=service_number)
        detail_items = make_list_of_detail_items(detail_item)

        note_1 = make_ticket_note(text=None, service_numbers=[service_number])
        note_2 = make_ticket_note(text=None, service_numbers=[service_number])
        ticket_notes = make_list_of_ticket_notes(note_1, note_2)

        ticket_details = make_ticket_details(detail_items=detail_items, notes=ticket_notes)

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        result = await service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number(
            tickets, service_number,
        )

        expected_notes = make_list_of_ticket_notes()
        expected = make_detail_item_with_notes_and_ticket_info(
            detail_item=detail_item, notes=expected_notes, ticket_info=ticket,
        )
        assert result == expected

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__valid_notes_found_for_serial_number_test(
            self, service_affecting_monitor, make_ticket, make_list_of_tickets, make_detail_item,
            make_list_of_detail_items, make_ticket_note, make_list_of_ticket_notes, make_ticket_details,
            make_detail_item_with_notes_and_ticket_info, make_rpc_response):
        service_number = 'VC1234567'

        ticket = make_ticket()
        tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=service_number)
        detail_items = make_list_of_detail_items(detail_item)

        note_1 = make_ticket_note(text="#*MetTel's IPA*#\nTrouble: Latency", service_numbers=[service_number])
        note_2 = make_ticket_note(text="#*MetTel's IPA*#\nTrouble: Jitter", service_numbers=[service_number])
        ticket_notes = make_list_of_ticket_notes(note_1, note_2)

        ticket_details = make_ticket_details(detail_items=detail_items, notes=ticket_notes)

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        result = await service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number(
            tickets, service_number,
        )

        expected = make_detail_item_with_notes_and_ticket_info(
            detail_item=detail_item, notes=ticket_notes, ticket_info=ticket,
        )
        assert result == expected

    @pytest.mark.asyncio
    async def append_latest_trouble_to_ticket__trouble_note_already_appended_after_ticket_creation_test(
            self, service_affecting_monitor, make_ticket_note, make_list_of_ticket_notes,
            make_detail_item_with_notes_and_ticket_info, make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        note_1 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: {trouble.value}")
        ticket_notes = make_list_of_ticket_notes(note_1)
        detail_info = make_detail_item_with_notes_and_ticket_info(notes=ticket_notes)

        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._append_latest_trouble_to_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_latest_trouble_to_ticket__trouble_note_already_appended_after_latest_reopen_test(
            self, service_affecting_monitor, make_ticket_note, make_list_of_ticket_notes,
            make_detail_item_with_notes_and_ticket_info, make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        note_1 = make_ticket_note(text=f"#*MetTel's IPA*#\nRe-opening ticket.\nTrouble: {trouble.value}")
        ticket_notes = make_list_of_ticket_notes(note_1)
        detail_info = make_detail_item_with_notes_and_ticket_info(notes=ticket_notes)

        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._append_latest_trouble_to_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_latest_trouble_to_ticket__current_env_is_not_production_test(
            self, service_affecting_monitor, make_ticket_note, make_list_of_ticket_notes,
            make_detail_item_with_notes_and_ticket_info, make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        note_1 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Packet Loss")
        ticket_notes = make_list_of_ticket_notes(note_1)
        detail_info = make_detail_item_with_notes_and_ticket_info(notes=ticket_notes)

        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._append_latest_trouble_to_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_latest_trouble_to_ticket__append_note_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_ticket_note, make_list_of_ticket_notes,
            make_detail_item_with_notes_and_ticket_info, make_structured_metrics_object_with_cache_and_contact_info,
            bruin_500_response):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        note_1 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Packet Loss")
        ticket_notes = make_list_of_ticket_notes(note_1)
        detail_info = make_detail_item_with_notes_and_ticket_info(notes=ticket_notes)

        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_500_response

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._append_latest_trouble_to_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_latest_trouble_to_ticket__trouble_note_appended_to_ticket_test(
            self, service_affecting_monitor, make_ticket_note, make_list_of_ticket_notes,
            make_detail_item_with_notes_and_ticket_info, make_structured_metrics_object_with_cache_and_contact_info,
            bruin_generic_200_response):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        note_1 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Packet Loss")
        ticket_notes = make_list_of_ticket_notes(note_1)
        detail_info = make_detail_item_with_notes_and_ticket_info(notes=ticket_notes)

        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._append_latest_trouble_to_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_note_append.assert_awaited_once()

    @pytest.mark.asyncio
    async def unresolve_task_for_affecting_ticket__current_env_is_not_production_test(
            self, service_affecting_monitor, make_detail_item_with_notes_and_ticket_info,
            make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        detail_info = make_detail_item_with_notes_and_ticket_info()
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._unresolve_task_for_affecting_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.open_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reopen.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def unresolve_task_for_affecting_ticket__reopen_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_detail_item_with_notes_and_ticket_info,
            make_structured_metrics_object_with_cache_and_contact_info, bruin_500_response):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        detail_info = make_detail_item_with_notes_and_ticket_info()
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.open_ticket.return_value = bruin_500_response

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._unresolve_task_for_affecting_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reopen.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def unresolve_task_for_affecting_ticket__ticket_task_reopened_test(
            self, service_affecting_monitor, make_detail_item_with_notes_and_ticket_info,
            make_structured_metrics_object_with_cache_and_contact_info, bruin_generic_200_response):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        detail_info = make_detail_item_with_notes_and_ticket_info()
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.open_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._unresolve_task_for_affecting_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_reopen.assert_awaited_once()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_called_once()

    @pytest.mark.asyncio
    async def create_affecting_ticket__current_env_is_not_production_test(
            self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def create_affecting_ticket__create_ticket_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info,
            bruin_500_response):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.create_affecting_ticket.return_value = bruin_500_response

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def create_affecting_ticket__ticket_created_test(
            self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info,
            bruin_generic_200_response, make_create_ticket_200_response):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.create_affecting_ticket.return_value = \
            make_create_ticket_200_response()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_awaited_once()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_called_once()

    def schedule_forward_to_hnoc_queue_test(self, service_affecting_monitor, frozen_datetime):
        ticket_id = 12345
        serial_number = 'VC1234567'

        current_datetime = frozen_datetime.now()
        wait_seconds_until_forward = service_affecting_monitor._config.MONITOR_CONFIG['forward_to_hnoc']
        forward_task_run_date = current_datetime + timedelta(seconds=wait_seconds_until_forward)

        with patch.multiple(service_affecting_monitor_module, datetime=frozen_datetime, timezone=Mock()):
            service_affecting_monitor._schedule_forward_to_hnoc_queue(
                ticket_id=ticket_id, serial_number=serial_number
            )

        service_affecting_monitor._scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._forward_ticket_to_hnoc_queue, 'date',
            kwargs={'ticket_id': ticket_id, 'serial_number': serial_number},
            run_date=forward_task_run_date,
            replace_existing=False,
            id=f'_forward_ticket_{ticket_id}_{serial_number}_to_hnoc',
        )

    @pytest.mark.asyncio
    async def forward_ticket_to_hnoc_queue__change_work_queue_request_has_not_2xx_status_test(
            self, service_affecting_monitor, bruin_500_response):
        ticket_id = 12345
        serial_number = 'VC1234567'

        service_affecting_monitor._bruin_repository.change_detail_work_queue_to_hnoc.return_value = \
            bruin_500_response

        await service_affecting_monitor._forward_ticket_to_hnoc_queue(ticket_id=ticket_id, serial_number=serial_number)

        service_affecting_monitor._bruin_repository.change_detail_work_queue_to_hnoc.assert_awaited_once_with(
            ticket_id=ticket_id, service_number=serial_number,
        )
        service_affecting_monitor._notifications_repository.notify_successful_ticket_forward.assert_not_awaited()

    @pytest.mark.asyncio
    async def forward_ticket_to_hnoc_queue__ticket_forwarded_to_queue_test(
            self, service_affecting_monitor, bruin_generic_200_response):
        ticket_id = 12345
        serial_number = 'VC1234567'

        service_affecting_monitor._bruin_repository.change_detail_work_queue_to_hnoc.return_value = \
            bruin_generic_200_response

        await service_affecting_monitor._forward_ticket_to_hnoc_queue(ticket_id=ticket_id, serial_number=serial_number)

        service_affecting_monitor._bruin_repository.change_detail_work_queue_to_hnoc.assert_awaited_once_with(
            ticket_id=ticket_id, service_number=serial_number,
        )
        service_affecting_monitor._notifications_repository.notify_successful_ticket_forward.assert_awaited_once_with(
            ticket_id=ticket_id, serial_number=serial_number,
        )

    @pytest.mark.asyncio
    async def run_autoresolve_process__no_metrics_found_test(
            self, service_affecting_monitor, make_list_of_link_metrics, make_rpc_response):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = \
            make_rpc_response(
                body=links_metrics,
                status=200,
            )

        await service_affecting_monitor._run_autoresolve_process()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._group_links_by_edge.assert_not_called()
        service_affecting_monitor._run_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_process__empty_dataset_after_structuring_and_crossing_info_and_grouping_by_edge_test(
            self, service_affecting_monitor, make_edge, make_link_with_edge_info, make_metrics_for_link,
            make_list_of_link_metrics, make_list_of_structured_metrics_objects,
            make_list_of_structured_metrics_objects_with_cache_and_contact_info, make_rpc_response):
        edge = make_edge(id_=0)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_structured_metrics = make_list_of_structured_metrics_objects()
        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._run_autoresolve_process()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_structured_metrics,
        )
        service_affecting_monitor._group_links_by_edge.assert_called_once_with(links_complete_info)
        service_affecting_monitor._run_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_process__autoresolve_triggers_test(
            self, service_affecting_monitor, make_cached_edge,
            make_customer_cache, make_edge, make_metrics, make_link_with_edge_info,
            make_metrics_for_link, make_list_of_link_metrics, make_structured_metrics_object,
            make_list_of_structured_metrics_objects, make_structured_metrics_object_with_cache_and_contact_info,
            make_list_of_structured_metrics_objects_with_cache_and_contact_info,
            make_rpc_response):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number, id_=edge_contact_info['edge_id'])
        edge_link_1_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_1_metrics = make_metrics()
        edge_link_1_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_1_with_edge_info, metrics=edge_link_1_metrics,
        )
        edge_link_2_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_2_metrics = make_metrics()
        edge_link_2_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_2_with_edge_info, metrics=edge_link_2_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_1_metric_set, edge_link_2_metric_set)

        link_1_structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=edge_link_1_metrics)
        link_2_structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=edge_link_2_metrics)
        links_structured_metrics_objects = make_list_of_structured_metrics_objects(
            link_1_structured_metrics_object, link_2_structured_metrics_object,
        )

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        link_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=link_1_structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
        )
        link_2_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=link_2_structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
        )
        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info(
            link_1_complete_info, link_2_complete_info,
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = \
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )

        await service_affecting_monitor._run_autoresolve_process()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_structured_metrics_objects,
        )
        service_affecting_monitor._group_links_by_edge.assert_called_once_with(links_complete_info)
        service_affecting_monitor._run_autoresolve_for_edge.assert_awaited_once()

    def group_links_by_edge_test(
            self, service_affecting_monitor, make_cached_edge,
            make_edge, make_link, make_metrics, make_structured_metrics_object,
            make_structured_metrics_object_with_cache_and_contact_info,
            make_list_of_structured_metrics_objects_with_cache_and_contact_info,
            make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_list_of_links_by_edge_objects):
        # Let's just pick an edge from the contact_info object to use it as a reference
        edge_contact_info = service_affecting_monitor._config.MONITOR_CONFIG['device_by_id'][0]

        edge_serial_number = edge_contact_info['serial']

        edge = make_edge(serial_number=edge_serial_number)
        link_1 = make_link()
        link_2 = make_link()

        edge_link_1_metrics = make_metrics()
        edge_link_2_metrics = make_metrics()

        link_1_structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=edge_link_1_metrics)
        link_2_structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=edge_link_2_metrics)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)

        link_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=link_1_structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
        )
        link_2_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=link_2_structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
        )
        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info(
            link_1_complete_info, link_2_complete_info,
        )

        result = service_affecting_monitor._group_links_by_edge(links_complete_info)

        link_1_status_and_metrics = make_link_status_and_metrics_object(link_info=link_1, metrics=edge_link_1_metrics)
        link_2_status_and_metrics = make_link_status_and_metrics_object(link_info=link_2, metrics=edge_link_2_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(
            link_1_status_and_metrics, link_2_status_and_metrics
        )
        links_grouped_by_edge_obj = make_links_by_edge_object(
            edge_info=edge,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info['contacts'],
            links=links_status_and_metrics,
        )
        expected = make_list_of_links_by_edge_objects(links_grouped_by_edge_obj)
        assert result == expected

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__not_all_metrics_within_thresholds_test(
            self, service_affecting_monitor, make_metrics, make_link_status_and_metrics_object,
            make_list_of_link_status_and_metrics_objects, make_links_by_edge_object):
        link_metrics = make_metrics(best_latency_ms_tx=9999, best_latency_ms_rx=0)
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(links=links_status_and_metrics)

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__get_open_tickets_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, bruin_500_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = bruin_500_response

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__empty_list_of_tickets_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_list_of_tickets, make_rpc_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        open_affecting_tickets = make_list_of_tickets()

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__ticket_not_created_by_automation_engine_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_rpc_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by='Travis Touchdown')
        open_affecting_tickets = make_list_of_tickets(ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__get_ticket_details_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_rpc_response,
            bruin_500_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by='Intelygenz Ai')
        open_affecting_tickets = make_list_of_tickets(ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = bruin_500_response

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__last_trouble_documented_on_ticket_creation_and_detected_long_ago_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_detail_item, make_list_of_detail_items,
            make_list_of_ticket_notes, make_ticket_details, make_rpc_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(
            created_by='Intelygenz Ai',
            create_date=str(datetime.now() - timedelta(days=30)),
        )
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        notes = make_list_of_ticket_notes()
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__last_trouble_documented_after_reopen_and_detected_long_ago_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_detail_item, make_list_of_detail_items,
            make_ticket_note, make_list_of_ticket_notes, make_ticket_details, make_rpc_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by='Intelygenz Ai')
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        note_1 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nTrouble: Latency",
            service_numbers=[serial_number],
            creation_date=str(datetime.now() - timedelta(days=30)),
        )
        notes = make_list_of_ticket_notes(note_1)
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__maximum_number_of_autoresolves_reached_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_detail_item, make_list_of_detail_items,
            make_ticket_note, make_list_of_ticket_notes, make_ticket_details, make_rpc_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by='Intelygenz Ai', create_date=str(datetime.now()))
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        note_1 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nAuto-resolving task for serial: {serial_number}",
            service_numbers=[serial_number],
        )
        note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nAuto-resolving task for serial: {serial_number}",
            service_numbers=[serial_number],
        )
        note_3 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nAuto-resolving task for serial: {serial_number}",
            service_numbers=[serial_number],
        )
        notes = make_list_of_ticket_notes(note_1, note_2, note_3)
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__task_for_serial_already_resolved_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_detail_item, make_list_of_detail_items,
            make_list_of_ticket_notes, make_ticket_details, make_rpc_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by='Intelygenz Ai', create_date=str(datetime.now()))
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=serial_number, status='R')
        detail_items = make_list_of_detail_items(detail_item)
        notes = make_list_of_ticket_notes()
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__current_env_is_not_production_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_detail_item, make_list_of_detail_items,
            make_list_of_ticket_notes, make_ticket_details, make_rpc_response):
        serial_number = 'VC1234567'
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by='Intelygenz Ai', create_date=str(datetime.now()))
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        notes = make_list_of_ticket_notes()
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__resolve_ticket_detail_request_has_not_2xx_status_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_detail_item, make_list_of_detail_items,
            make_list_of_ticket_notes, make_ticket_details, make_rpc_response, bruin_500_response):
        serial_number = 'VC1234567'
        client_id = 12345
        ticket_id = 123
        ticket_detail_id = 456

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(ticket_id=ticket_id, created_by='Intelygenz Ai', create_date=str(datetime.now()))
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(id_=ticket_detail_id, value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        notes = make_list_of_ticket_notes()
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.return_value = bruin_500_response

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            ticket_id, serial_number,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_awaited_once_with(
            ticket_id, ticket_detail_id,
        )
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__ticket_task_autoresolved_test(
            self, service_affecting_monitor, make_cached_edge, make_bruin_client_info,
            make_metrics, make_link_status_and_metrics_object, make_list_of_link_status_and_metrics_objects,
            make_links_by_edge_object, make_ticket, make_list_of_tickets, make_detail_item, make_list_of_detail_items,
            make_list_of_ticket_notes, make_ticket_details, make_rpc_response, bruin_generic_200_response):
        serial_number = 'VC1234567'
        client_id = 12345
        ticket_id = 123
        ticket_detail_id = 456

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0, best_latency_ms_rx=0,
            best_packet_loss_tx=0, best_packet_loss_rx=0,
            best_jitter_ms_tx=0, best_jitter_ms_rx=0,
            bytes_tx=1, bytes_rx=1,
            bps_of_best_path_tx=100, bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info, links=links_status_and_metrics,
        )

        ticket = make_ticket(ticket_id=ticket_id, created_by='Intelygenz Ai', create_date=str(datetime.now()))
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(id_=ticket_detail_id, value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        notes = make_list_of_ticket_notes()
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.return_value = bruin_generic_200_response

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            ticket_id, serial_number,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_awaited_once_with(
            ticket_id, ticket_detail_id,
        )
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_awaited_once_with(
            ticket_id, serial_number,
        )
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_awaited_once_with(
            ticket_id, serial_number,
        )
