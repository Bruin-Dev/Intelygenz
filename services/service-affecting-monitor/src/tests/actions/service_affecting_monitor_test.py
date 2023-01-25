import json
import os
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from application import REMINDER_NOTE_REGEX, AffectingTroubles, ForwardQueues
from application.actions import service_affecting_monitor as service_affecting_monitor_module
from application.repositories import utils_repository as utils_repository_module
from apscheduler.util import undefined
from config import testconfig
from framework.storage.task_dispatcher_client import TaskTypes
from nats.aio.msg import Msg
from shortuuid import uuid
from tests.fixtures._constants import CURRENT_DATETIME

uuid_ = uuid()
uuid_mock = patch.object(service_affecting_monitor_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class TestServiceAffectingMonitor:
    def instance_test(
        self,
        service_affecting_monitor,
        scheduler,
        customer_cache_repository,
        bruin_repository,
        velocloud_repository,
        notifications_repository,
        ticket_repository,
        trouble_repository,
        metrics_repository,
        utils_repository,
    ):
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
            service_affecting_monitor._service_affecting_monitor_process,
            "interval",
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_service_affecting_monitor_process",
        )

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job__no_exec_on_start_test(self, service_affecting_monitor):
        await service_affecting_monitor.start_service_affecting_monitor(exec_on_start=False)

        service_affecting_monitor._scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._service_affecting_monitor_process,
            "interval",
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=undefined,
            replace_existing=False,
            id="_service_affecting_monitor_process",
        )

    @pytest.mark.asyncio
    async def service_affecting_monitor_process__get_cache_request_has_202_status_test(
        self, service_affecting_monitor, get_customer_cache_202_response
    ):
        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = (
            get_customer_cache_202_response
        )

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
        self, service_affecting_monitor, get_customer_cache_404_response
    ):
        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = (
            get_customer_cache_404_response
        )

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
        self, service_affecting_monitor, get_customer_cache_empty_response
    ):
        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.return_value = (
            get_customer_cache_empty_response
        )

        await service_affecting_monitor._service_affecting_monitor_process()

        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_not_awaited()
        service_affecting_monitor._packet_loss_check.assert_not_awaited()
        service_affecting_monitor._jitter_check.assert_not_awaited()
        service_affecting_monitor._bandwidth_check.assert_not_awaited()
        service_affecting_monitor._run_autoresolve_process.assert_not_awaited()
        assert service_affecting_monitor._customer_cache == []

    @pytest.mark.asyncio
    async def service_affecting_monitor_process__ok_test(
        self,
        service_affecting_monitor,
        make_customer_cache,
        make_cached_edge,
        make_bruin_client_info,
        make_contact_info,
        make_rpc_response,
    ):
        client_1_id = 83109
        client_2_id = 88480

        edge_bruin_client_info_1 = make_bruin_client_info(client_id=client_1_id)
        edge_bruin_client_info_2 = make_bruin_client_info(client_id=client_2_id)

        edge_1 = make_cached_edge(bruin_client_info=edge_bruin_client_info_1)
        edge_2 = make_cached_edge(bruin_client_info=edge_bruin_client_info_2)
        customer_cache = make_customer_cache(edge_1, edge_2)

        get_cache_response = make_rpc_response(
            body=customer_cache,
            status=200,
        )

        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring = AsyncMock(
            return_value=get_cache_response
        )

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config["contact_info_by_host_and_client_id"] = {
            "test-host": {
                client_1_id: make_contact_info(),
                client_2_id: make_contact_info(),
            }
        }
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._service_affecting_monitor_process()

        service_affecting_monitor._customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_awaited_once()
        service_affecting_monitor._packet_loss_check.assert_awaited_once()
        service_affecting_monitor._jitter_check.assert_awaited_once()
        service_affecting_monitor._bandwidth_check.assert_awaited_once()
        service_affecting_monitor._run_autoresolve_process.assert_awaited_once()
        assert service_affecting_monitor._customer_cache == customer_cache

    def structure_links_metrics__ok_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link,
        make_metrics,
        make_link_with_edge_info,
        make_link_with_metrics,
        make_metrics_for_link,
        make_list_of_links_with_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
    ):
        link_1_id = 1
        link_2_id = 2

        metric_set_1 = make_metrics()
        metric_set_2 = make_metrics()

        edge = make_edge(edge_state="CONNECTED")
        link_1 = make_link(id_=link_1_id)
        link_2 = make_link(id_=link_2_id)
        metric_set_1_with_link_1_info = make_metrics_for_link(link_id=link_1, metrics=metric_set_1)
        metric_set_2_with_link_2_info = make_metrics_for_link(link_id=link_2, metrics=metric_set_2)

        link_1_with_edge_info = make_link_with_edge_info(link_info=link_1, edge_info=edge)
        link_2_with_edge_info = make_link_with_edge_info(link_info=link_2, edge_info=edge)
        link_1_info_with_metrics = make_link_with_metrics(
            link_info=link_1_with_edge_info,
            metrics=metric_set_1_with_link_1_info,
        )
        link_2_info_with_metrics = make_link_with_metrics(
            link_info=link_2_with_edge_info,
            metrics=metric_set_2_with_link_2_info,
        )
        links_info_with_metrics = make_list_of_links_with_metrics(link_1_info_with_metrics, link_2_info_with_metrics)

        result = service_affecting_monitor._structure_links_metrics(links_info_with_metrics)

        structured_metrics_1 = make_structured_metrics_object(edge_info=edge, link_info=link_1, metrics=metric_set_1)
        structured_metrics_2 = make_structured_metrics_object(edge_info=edge, link_info=link_2, metrics=metric_set_2)
        expected = make_list_of_structured_metrics_objects(structured_metrics_1, structured_metrics_2)
        assert result == expected

    def structure_links_metrics__invalid_edge_state_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link,
        make_metrics,
        make_link_with_edge_info,
        make_link_with_metrics,
        make_metrics_for_link,
        make_list_of_links_with_metrics,
    ):
        link_1_id = 1
        link_2_id = 2

        metric_set_1 = make_metrics()
        metric_set_2 = make_metrics()

        edge = make_edge(edge_state=None)
        link_1 = make_link(id_=link_1_id)
        link_2 = make_link(id_=link_2_id)
        metric_set_1_with_link_1_info = make_metrics_for_link(link_id=link_1, metrics=metric_set_1)
        metric_set_2_with_link_2_info = make_metrics_for_link(link_id=link_2, metrics=metric_set_2)

        link_1_with_edge_info = make_link_with_edge_info(link_info=link_1, edge_info=edge)
        link_2_with_edge_info = make_link_with_edge_info(link_info=link_2, edge_info=edge)
        link_1_info_with_metrics = make_link_with_metrics(
            link_info=link_1_with_edge_info,
            metrics=metric_set_1_with_link_1_info,
        )
        link_2_info_with_metrics = make_link_with_metrics(
            link_info=link_2_with_edge_info,
            metrics=metric_set_2_with_link_2_info,
        )
        links_info_with_metrics = make_list_of_links_with_metrics(link_1_info_with_metrics, link_2_info_with_metrics)

        result = service_affecting_monitor._structure_links_metrics(links_info_with_metrics)

        expected = []
        assert result == expected

    def structure_links_metrics__edge_not_activated_yet_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link,
        make_metrics,
        make_link_with_edge_info,
        make_link_with_metrics,
        make_metrics_for_link,
        make_list_of_links_with_metrics,
    ):
        link_1_id = 1
        link_2_id = 2

        metric_set_1 = make_metrics()
        metric_set_2 = make_metrics()

        edge = make_edge(edge_state="NEVER_ACTIVATED")
        link_1 = make_link(id_=link_1_id)
        link_2 = make_link(id_=link_2_id)
        metric_set_1_with_link_1_info = make_metrics_for_link(link_id=link_1, metrics=metric_set_1)
        metric_set_2_with_link_2_info = make_metrics_for_link(link_id=link_2, metrics=metric_set_2)

        link_1_with_edge_info = make_link_with_edge_info(link_info=link_1, edge_info=edge)
        link_2_with_edge_info = make_link_with_edge_info(link_info=link_2, edge_info=edge)
        link_1_info_with_metrics = make_link_with_metrics(
            link_info=link_1_with_edge_info,
            metrics=metric_set_1_with_link_1_info,
        )
        link_2_info_with_metrics = make_link_with_metrics(
            link_info=link_2_with_edge_info,
            metrics=metric_set_2_with_link_2_info,
        )
        links_info_with_metrics = make_list_of_links_with_metrics(link_1_info_with_metrics, link_2_info_with_metrics)

        result = service_affecting_monitor._structure_links_metrics(links_info_with_metrics)

        expected = []
        assert result == expected

    @pytest.mark.asyncio
    async def map_cached_edges_with_links_metrics_and_contact_info__specific_site_contacts_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_contact_info,
        make_site_details,
    ):
        site_detail_email = "test@email.com"
        site_detail_phone = "510-111-111"
        site_detail_name = "Help Desk"
        site_details = make_site_details(
            contact_name=site_detail_name,
            contact_phone=site_detail_phone,
            contact_email=site_detail_email,
        )

        edge_contact_info = make_contact_info(email=site_detail_email, phone=site_detail_phone, name=site_detail_name)

        edge_1_serial_number = "VCO123"

        edge_1_cache_info = make_cached_edge(serial_number=edge_1_serial_number, site_details=site_details)
        edge_1 = make_edge(serial_number=edge_1_serial_number)

        edge_1_structured_metrics = make_structured_metrics_object(edge_info=edge_1)
        structured_metrics = make_list_of_structured_metrics_objects(edge_1_structured_metrics)

        customer_cache = make_customer_cache(edge_1_cache_info)
        service_affecting_monitor._customer_cache = customer_cache

        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        result = await service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info(
            structured_metrics
        )

        edge_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=edge_1_structured_metrics,
            cache_info=edge_1_cache_info,
            contact_info=edge_contact_info,
        )

        expected = make_list_of_structured_metrics_objects_with_cache_and_contact_info(edge_1_complete_info)
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.assert_called_once_with(site_details)

        assert result == expected

    @pytest.mark.asyncio
    async def map_cached_edges_with_links_metrics_and_contact_info__default_contacts_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_contact_info,
        make_site_details,
        make_bruin_client_info,
    ):
        site_detail_email = None
        site_detail_phone = None
        site_detail_name = None
        site_details = make_site_details(
            contact_name=site_detail_name,
            contact_phone=site_detail_phone,
            contact_email=site_detail_email,
        )

        edge_1_serial_number = "VCO123"

        client_id = 12345
        default_contact_info = make_contact_info(
            email="some-email",
            phone="some-phone",
            name="some-name",
        )

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_1_cache_info = make_cached_edge(
            serial_number=edge_1_serial_number,
            bruin_client_info=bruin_client_info,
            site_details=site_details,
        )
        edge_1 = make_edge(serial_number=edge_1_serial_number)

        edge_1_structured_metrics = make_structured_metrics_object(edge_info=edge_1)
        structured_metrics = make_list_of_structured_metrics_objects(edge_1_structured_metrics)

        customer_cache = make_customer_cache(edge_1_cache_info)
        service_affecting_monitor._customer_cache = customer_cache

        contact_info_by_client_id = {
            client_id: default_contact_info,
        }
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        result = await service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info(
            structured_metrics
        )

        edge_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=edge_1_structured_metrics,
            cache_info=edge_1_cache_info,
            contact_info=default_contact_info,
        )

        expected = make_list_of_structured_metrics_objects_with_cache_and_contact_info(edge_1_complete_info)
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.assert_called_once_with(site_details)

        assert result == expected

    @pytest.mark.asyncio
    async def map_cached_edges_with_links_metrics_and_contact_info__force_default_contacts_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_contact_info,
        make_site_details,
        make_bruin_client_info,
        make_edge_full_id,
    ):
        site_detail_email = None
        site_detail_phone = None
        site_detail_name = None
        site_details = make_site_details(
            contact_name=site_detail_name,
            contact_phone=site_detail_phone,
            contact_email=site_detail_email,
        )

        edge_1_serial_number = "VCO123"
        edge_2_serial_number = "VC4567"

        client_id_1 = 1
        client_id_2 = 2
        default_contact_info = make_contact_info(
            email="some-email",
            phone="some-phone",
            name="some-name",
        )

        bruin_client_info_1 = make_bruin_client_info(client_id=client_id_1)
        bruin_client_info_2 = make_bruin_client_info(client_id=client_id_2)
        edge_1_cache_info = make_cached_edge(
            serial_number=edge_1_serial_number,
            bruin_client_info=bruin_client_info_1,
            site_details=site_details,
        )
        full_id = make_edge_full_id(host="host-2")
        edge_2_cache_info = make_cached_edge(
            full_id=full_id,
            serial_number=edge_2_serial_number,
            bruin_client_info=bruin_client_info_2,
            site_details=site_details,
        )
        edge_1 = make_edge(serial_number=edge_1_serial_number)
        edge_2 = make_edge(serial_number=edge_2_serial_number)

        edge_1_structured_metrics = make_structured_metrics_object(edge_info=edge_1)
        edge_2_structured_metrics = make_structured_metrics_object(edge_info=edge_2)
        structured_metrics = make_list_of_structured_metrics_objects(
            edge_1_structured_metrics,
            edge_2_structured_metrics,
        )

        customer_cache = make_customer_cache(edge_1_cache_info, edge_2_cache_info)
        service_affecting_monitor._customer_cache = customer_cache

        contact_info_by_client_id = {
            client_id_1: default_contact_info,
            client_id_2: default_contact_info,
        }
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        result = await service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info(
            structured_metrics
        )

        edge_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=edge_1_structured_metrics,
            cache_info=edge_1_cache_info,
            contact_info=default_contact_info,
        )
        edge_2_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=edge_2_structured_metrics,
            cache_info=edge_2_cache_info,
            contact_info=default_contact_info,
        )

        expected = make_list_of_structured_metrics_objects_with_cache_and_contact_info(
            edge_1_complete_info,
            edge_2_complete_info,
        )
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.assert_not_called()

        assert result == expected

    @pytest.mark.asyncio
    async def map_cached_edges_with_links_metrics_and_contact_info__no_cached_edge_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link,
        make_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_cached_edge,
        make_customer_cache,
        make_site_details,
    ):
        site_detail_email = "test@email.com"
        site_detail_phone = "510-111-111"
        site_detail_name = "Help Desk"
        site_details = make_site_details(
            contact_name=site_detail_name,
            contact_phone=site_detail_phone,
            contact_email=site_detail_email,
        )

        edge_1_serial_number = "VCO123"
        edge_2_serial_number = "VCO1234"

        edge = make_edge(serial_number=edge_1_serial_number)
        link_1 = make_link()

        link_1_metric_set = make_metrics()

        structured_metrics_1 = make_structured_metrics_object(
            edge_info=edge,
            link_info=link_1,
            metrics=link_1_metric_set,
        )
        structured_metrics = make_list_of_structured_metrics_objects(structured_metrics_1)

        edge_1_cache_info = make_cached_edge(serial_number=edge_2_serial_number, site_details=site_details)
        customer_cache = make_customer_cache(edge_1_cache_info)
        service_affecting_monitor._customer_cache = customer_cache

        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        result = await service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info(
            structured_metrics
        )

        service_affecting_monitor._bruin_repository.get_contact_info_for_site.assert_not_called()
        expected = []
        assert result == expected

    @pytest.mark.asyncio
    async def latency_check__no_metrics_found_test(
        self, service_affecting_monitor, make_list_of_link_metrics, make_rpc_response
    ):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_latency_checks.return_value = (
            make_rpc_response(
                body=links_metrics,
                status=200,
            )
        )

        await service_affecting_monitor._latency_check()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_latency_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check__empty_dataset_after_structuring_and_crossing_info_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_rpc_response,
    ):
        edge = make_edge(edge_state=None)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_latency_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._latency_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_complete_info,
        )
        service_affecting_monitor._process_latency_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check__all_metrics_within_thresholds_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"

        edge = make_edge(serial_number=edge_serial_number)
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_latency_ms_tx=0, best_latency_ms_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_latency_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._latency_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_latency_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check__trouble_detected_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()

        edge_serial_number = "VCO123"

        edge = make_edge(serial_number=edge_serial_number)
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
            contact_info=edge_contact_info,
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_latency_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._latency_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_latency_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def packet_loss_check__no_metrics_found_test(
        self, service_affecting_monitor, make_list_of_link_metrics, make_rpc_response
    ):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_packet_loss_checks.return_value = (
            make_rpc_response(
                body=links_metrics,
                status=200,
            )
        )

        await service_affecting_monitor._packet_loss_check()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_packet_loss_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check__empty_dataset_after_structuring_and_crossing_info_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_rpc_response,
    ):
        edge = make_edge(edge_state=None)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_packet_loss_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._packet_loss_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_complete_info,
        )
        service_affecting_monitor._process_packet_loss_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check__all_metrics_within_thresholds_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"

        edge = make_edge(serial_number=edge_serial_number)
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_packet_loss_tx=0, best_packet_loss_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_packet_loss_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._packet_loss_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_packet_loss_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check__trouble_detected_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"

        edge = make_edge(serial_number=edge_serial_number)
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
            contact_info=edge_contact_info,
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_packet_loss_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._packet_loss_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_packet_loss_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def jitter_check__no_metrics_found_test(
        self, service_affecting_monitor, make_list_of_link_metrics, make_rpc_response
    ):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_jitter_checks.return_value = (
            make_rpc_response(
                body=links_metrics,
                status=200,
            )
        )

        await service_affecting_monitor._jitter_check()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_jitter_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def jitter_check__empty_dataset_after_structuring_and_crossing_info_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_rpc_response,
    ):
        edge = make_edge(edge_state=None)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_jitter_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._jitter_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_complete_info,
        )
        service_affecting_monitor._process_jitter_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def jitter_check__all_metrics_within_thresholds_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"

        edge = make_edge(serial_number=edge_serial_number)
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        metrics = make_metrics(best_jitter_ms_tx=0, best_jitter_ms_rx=0)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info, metrics=metrics)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_jitter_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._jitter_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_jitter_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def jitter_check__trouble_detected_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"

        edge = make_edge(serial_number=edge_serial_number)
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
            contact_info=edge_contact_info,
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_jitter_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._jitter_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_jitter_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def bandwidth_check__no_metrics_found_test(
        self, service_affecting_monitor, make_list_of_link_metrics, make_rpc_response
    ):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = (
            make_rpc_response(
                body=links_metrics,
                status=200,
            )
        )

        await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__empty_dataset_after_structuring_and_crossing_info_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_list_of_structured_metrics_objects,
        make_rpc_response,
    ):
        edge = make_edge(edge_state=None)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_structured_metrics = make_list_of_structured_metrics_objects()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_structured_metrics,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__unmonitorized_bruin_clients_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"
        client_id = 1234

        edge = make_edge(serial_number=edge_serial_number)
        edge_link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_metrics = make_metrics()
        edge_link_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_with_edge_info,
            metrics=edge_link_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=edge_link_metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=edge_serial_number, bruin_client_info=edge_bruin_client_info)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config["customers_with_bandwidth_enabled"] = []
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__invalid_tx_and_rx_bandwidth_metrics_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"
        client_id = 1234

        edge = make_edge(serial_number=edge_serial_number)
        edge_link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_metrics = make_metrics(bps_of_best_path_tx=0, bps_of_best_path_rx=0)
        edge_link_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_with_edge_info,
            metrics=edge_link_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_metric_set)

        structured_metrics_object = make_structured_metrics_object(edge_info=edge, metrics=edge_link_metrics)
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=edge_serial_number, bruin_client_info=edge_bruin_client_info)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config["customers_with_bandwidth_enabled"] = [client_id]
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__all_metrics_within_thresholds_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"
        client_id = 1234

        edge = make_edge(serial_number=edge_serial_number)
        edge_link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_metrics = make_metrics(bps_of_best_path_tx=100, bps_of_best_path_rx=100)
        edge_link_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_with_edge_info,
            metrics=edge_link_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_metric_set)

        structured_metrics_object = make_structured_metrics_object(
            edge_info=edge,
            metrics=edge_link_metrics,
        )
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=edge_serial_number, bruin_client_info=edge_bruin_client_info)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config["customers_with_bandwidth_enabled"] = [client_id]
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check__trouble_detected_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_customer_cache,
        make_edge,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"
        client_id = 12345

        edge = make_edge(serial_number=edge_serial_number)
        edge_link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        edge_link_metrics = make_metrics(
            bytes_tx=999999,
            bytes_rx=999999,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        edge_link_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_with_edge_info,
            metrics=edge_link_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_metric_set)

        structured_metrics_object = make_structured_metrics_object(
            edge_info=edge,
            metrics=edge_link_metrics,
        )
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=edge_serial_number, bruin_client_info=edge_bruin_client_info)
        customer_cache = make_customer_cache(edge_cache_info)

        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info,
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bandwidth_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        custom_monitor_config = service_affecting_monitor._config.MONITOR_CONFIG.copy()
        custom_monitor_config["customers_with_bandwidth_enabled"] = [client_id]
        with patch.dict(service_affecting_monitor._config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._bandwidth_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bandwidth_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def bouncing_check__no_metrics_found_test(
        self, service_affecting_monitor, make_list_of_link_metrics, make_rpc_response
    ):
        links_metrics = make_list_of_link_metrics()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bouncing_checks.return_value = (
            make_rpc_response(
                body=links_metrics,
                status=200,
            )
        )

        await service_affecting_monitor._bouncing_check()

        service_affecting_monitor._velocloud_repository.get_events_by_serial_and_interface.assert_not_called()
        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._process_bouncing_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bouncing_check__empty_dataset_after_structuring_and_crossing_info_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_events_by_serial_and_interface,
        make_rpc_response,
    ):
        edge = make_edge(edge_state=None)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)
        events_by_serial_and_interface = make_events_by_serial_and_interface()

        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bouncing_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._bouncing_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(
            links_metric_sets, events_by_serial_and_interface
        )
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_complete_info,
        )
        service_affecting_monitor._process_bouncing_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bouncing_check__events_within_threshold_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_link,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_event,
        make_events_by_serial_and_interface,
        make_structured_metrics_object_with_events,
        make_list_of_structured_metrics_objects,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"
        interface = "GE1"

        edge = make_edge(serial_number=edge_serial_number, edge_state="CONNECTED")
        link = make_link(interface=interface)
        link_with_edge_info = make_link_with_edge_info(edge_info=edge, link_info=link)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        event = make_event()
        events = [event]
        events_by_serial_and_interface = make_events_by_serial_and_interface()
        events_by_serial_and_interface[edge_serial_number][interface] = events
        structured_metrics_object = make_structured_metrics_object_with_events(
            edge_info=edge, link_info=link, events=events
        )
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bouncing_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        service_affecting_monitor._velocloud_repository.get_events_by_serial_and_interface.return_value = (
            events_by_serial_and_interface
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._bouncing_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(
            links_metric_sets, events_by_serial_and_interface
        )
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bouncing_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bouncing_check__trouble_detected_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_link,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_event,
        make_events_by_serial_and_interface,
        make_structured_metrics_object_with_events,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"
        interface = "GE1"

        edge = make_edge(serial_number=edge_serial_number, edge_state="CONNECTED")
        link = make_link(interface=interface)
        link_with_edge_info = make_link_with_edge_info(edge_info=edge, link_info=link)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        event = make_event()
        events = [event] * 10
        events_by_serial_and_interface = make_events_by_serial_and_interface(
            serials=[edge_serial_number], interfaces=[interface]
        )
        events_by_serial_and_interface[edge_serial_number][interface] = events
        structured_metrics_object = make_structured_metrics_object_with_events(
            edge_info=edge, link_info=link, events=events
        )
        structured_metrics_objects = make_list_of_structured_metrics_objects(structured_metrics_object)

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        link_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info,
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_bouncing_checks.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        service_affecting_monitor._velocloud_repository.get_events_by_serial_and_interface.return_value = (
            events_by_serial_and_interface
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._bouncing_check()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(
            links_metric_sets, events_by_serial_and_interface
        )
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_metrics_objects,
        )
        service_affecting_monitor._process_bouncing_trouble.assert_awaited_once_with(link_complete_info)

    @pytest.mark.asyncio
    async def process_latency_trouble_test(
        self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info
    ):
        trouble = AffectingTroubles.LATENCY
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_latency_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)

    @pytest.mark.asyncio
    async def process_jitter_trouble_test(
        self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info
    ):
        trouble = AffectingTroubles.JITTER
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_jitter_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)

    @pytest.mark.asyncio
    async def process_packet_loss_trouble_test(
        self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info
    ):
        trouble = AffectingTroubles.PACKET_LOSS
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_packet_loss_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)

    @pytest.mark.asyncio
    async def process_bandwidth_trouble_test(
        self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info
    ):
        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_bandwidth_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)

    @pytest.mark.asyncio
    async def process_bouncing_trouble_test(
        self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info
    ):
        trouble = AffectingTroubles.BOUNCING
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        await service_affecting_monitor._process_bouncing_trouble(link_info)

        service_affecting_monitor._process_affecting_trouble.assert_awaited_once_with(link_info, trouble)
        service_affecting_monitor._attempt_forward_to_asr.assert_awaited_once_with(link_info, trouble, None)

    @pytest.mark.asyncio
    async def process_affecting_trouble__get_open_affecting_tickets_request_has_not_2xx_status_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_cached_edge,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_500_response,
    ):
        service_number = "VC1234567"
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = bruin_500_response

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._should_forward_to_hnoc.assert_not_called()
        service_affecting_monitor._send_reminder.assert_not_awaited()
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__open_ticket_found_with_resolved_detail_for_serial_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_cached_edge,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
        make_rpc_response,
    ):
        service_number = "VC1234567"
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        ticket = make_ticket()
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(status="R")  # Resolved
        detail_object = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, ticket_info=ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = detail_object

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._should_forward_to_hnoc.assert_not_called()
        service_affecting_monitor._send_reminder.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_awaited_once_with(
            detail_object,
            trouble,
            link_info,
        )
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__open_ticket_found_with_in_progress_detail_for_serial_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_cached_edge,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
        make_rpc_response,
    ):
        service_number = "VC1234567"
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        ticket = make_ticket()
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(status="I")  # In progress
        detail_object = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, ticket_info=ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = detail_object

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._should_forward_to_hnoc.assert_called()
        service_affecting_monitor._send_reminder.assert_not_awaited()
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_awaited_once_with(
            detail_object,
            trouble,
            link_info,
        )
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__open_ticket_found_with_in_progress_detail_for_serial_send_reminder_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_cached_edge,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
        make_rpc_response,
    ):
        service_number = "VC1234567"
        client_id = 12345
        ticket_id = 123
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)
        ticket = make_ticket(ticket_id=ticket_id)
        open_affecting_tickets = make_list_of_tickets(ticket)
        detail_item = make_detail_item(status="I")
        detail_object = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, ticket_info=ticket)
        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = detail_object
        service_affecting_monitor._should_forward_to_hnoc.return_value = False

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_awaited_once_with(
            detail_object,
            trouble,
            link_info,
        )
        service_affecting_monitor._should_forward_to_hnoc.assert_called()
        service_affecting_monitor._send_reminder.assert_awaited_once_with(detail_object)
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__get_resolved_affecting_tickets_request_has_not_2xx_status_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_cached_edge,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_list_of_tickets,
        make_rpc_response,
        bruin_500_response,
    ):
        service_number = "VC1234567"
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(cache_info=edge_cache_info)

        open_affecting_tickets = make_list_of_tickets()

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.return_value = bruin_500_response
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = (
            None  # No Open ticket was found
        )

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._should_forward_to_hnoc.assert_not_called()
        service_affecting_monitor._send_reminder.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_affecting_trouble__resolved_ticket_found_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_cached_edge,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
        make_rpc_response,
    ):
        service_number = "VC1234567"
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
            None,  # No Open ticket was found
            detail_object,  # Resolved ticket was found
        ]

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._should_forward_to_hnoc.assert_not_called()
        service_affecting_monitor._send_reminder.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_awaited_once_with(
            detail_object,
            trouble,
            link_info,
        )
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

    # @pytest.mark.asyncio
    # async def fail_test(self):
    #     assert True is False

    @pytest.mark.asyncio
    async def process_affecting_trouble__byob_link_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_cached_edge,
        make_structured_metrics_object_with_cache_and_contact_info,
        # make_structured_metrics_object,
        # make_link
    ):
        # assert True is False
        # link_id = 1
        # link_display_name = 'byod'
        service_number = "VC1234567"
        client_id = 12345
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        # metrics_object = make_structured_metrics_object()
            # link_info=make_link(
            #     id=link_id, 
            #     display_name=link_display_name))

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=service_number, bruin_client_info=bruin_client_info)
        link_info = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=edge_cache_info)
            # ,
            # metrics_object=metrics_object)

        service_affecting_monitor._is_link_label_blacklisted_from_hnoc.return_value = True

        result = await service_affecting_monitor._process_affecting_trouble(link_info, trouble)
        
        service_affecting_monitor._create_affecting_ticket.assert_not_awaited()

        assert result is None


    @pytest.mark.asyncio
    async def process_affecting_trouble__no_open_or_resolved_ticket_found_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_cached_edge,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_list_of_tickets,
        make_rpc_response,
    ):
        service_number = "VC1234567"
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
        service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number.return_value = (
            None  # No Open or Resolved tickets found
        )

        await service_affecting_monitor._process_affecting_trouble(link_info, trouble)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._bruin_repository.get_resolved_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=service_number,
        )
        service_affecting_monitor._append_latest_trouble_to_ticket.assert_not_awaited()
        service_affecting_monitor._should_forward_to_hnoc.assert_not_called()
        service_affecting_monitor._send_reminder.assert_not_awaited()
        service_affecting_monitor._unresolve_task_for_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._create_affecting_ticket.assert_awaited_once_with(trouble, link_info)

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__empty_list_of_tickets_test(
        self, service_affecting_monitor, make_ticket, make_list_of_tickets, bruin_500_response
    ):
        service_number = "VC1234567"

        tickets = make_list_of_tickets()

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = bruin_500_response

        result = await service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number(
            tickets,
            service_number,
        )
        assert result is None

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__get_details_request_has_not_2xx_status_test(
        self, service_affecting_monitor, make_ticket, make_list_of_tickets, bruin_500_response
    ):
        service_number = "VC1234567"

        ticket = make_ticket()
        tickets = make_list_of_tickets(ticket)

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = bruin_500_response

        result = await service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number(
            tickets,
            service_number,
        )
        assert result is None

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__no_notes_found_for_serial_number_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        service_number = "VC1234567"
        fake_service_number = "VC0000000"

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
            tickets,
            service_number,
        )

        assert result is None

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__invalid_notes_found_for_serial_number_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        service_number = "VC1234567"

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
            tickets,
            service_number,
        )

        assert result is None

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__unrelated_notes_found_for_serial_number_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        service_number = "VC1234567"

        ticket = make_ticket()
        tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=service_number)
        detail_items = make_list_of_detail_items(detail_item)

        note_1 = make_ticket_note(text="#*MetTel's IPA*#\nPossible Fraud", service_numbers=[service_number])
        note_2 = make_ticket_note(text="#*MetTel's IPA*#\nPossible Fraud", service_numbers=[service_number])
        ticket_notes = make_list_of_ticket_notes(note_1, note_2)

        ticket_details = make_ticket_details(detail_items=detail_items, notes=ticket_notes)

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        result = await service_affecting_monitor._get_oldest_affecting_ticket_for_serial_number(
            tickets,
            service_number,
        )

        assert result is None

    @pytest.mark.asyncio
    async def get_oldest_affecting_ticket_for_serial_number__valid_notes_found_for_serial_number_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_detail_item_with_notes_and_ticket_info,
        make_rpc_response,
    ):
        service_number = "VC1234567"

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
            tickets,
            service_number,
        )

        expected = make_detail_item_with_notes_and_ticket_info(
            detail_item=detail_item,
            notes=ticket_notes,
            ticket_info=ticket,
        )
        assert result == expected

    @pytest.mark.asyncio
    async def append_latest_trouble_to_ticket__trouble_note_already_appended_after_ticket_creation_test(
        self,
        service_affecting_monitor,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
    ):
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
        self,
        service_affecting_monitor,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
    ):
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
        self,
        service_affecting_monitor,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        note_1 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Packet Loss")
        ticket_notes = make_list_of_ticket_notes(note_1)
        detail_info = make_detail_item_with_notes_and_ticket_info(notes=ticket_notes)

        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "dev"):
            await service_affecting_monitor._append_latest_trouble_to_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_latest_trouble_to_ticket__append_note_request_has_not_2xx_status_test(
        self,
        service_affecting_monitor,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_500_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        note_1 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Packet Loss")
        ticket_notes = make_list_of_ticket_notes(note_1)
        detail_info = make_detail_item_with_notes_and_ticket_info(notes=ticket_notes)

        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_500_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._append_latest_trouble_to_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_latest_trouble_to_ticket__trouble_note_appended_to_ticket_test(
        self,
        service_affecting_monitor,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_generic_200_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        note_1 = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Packet Loss")
        ticket_notes = make_list_of_ticket_notes(note_1)
        detail_info = make_detail_item_with_notes_and_ticket_info(notes=ticket_notes)

        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._append_latest_trouble_to_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_note_append.assert_awaited_once()

    @pytest.mark.asyncio
    async def unresolve_task_for_affecting_ticket__current_env_is_not_production_test(
        self,
        service_affecting_monitor,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        detail_info = make_detail_item_with_notes_and_ticket_info()
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "dev"):
            await service_affecting_monitor._unresolve_task_for_affecting_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.open_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reopen.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def unresolve_task_for_affecting_ticket__reopen_request_has_not_2xx_status_test(
        self,
        service_affecting_monitor,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_500_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        detail_info = make_detail_item_with_notes_and_ticket_info()
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.open_ticket.return_value = bruin_500_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._unresolve_task_for_affecting_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reopen.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def unresolve_task_for_affecting_ticket__dont_schedule_forward_to_hnoc_test(
        self,
        service_affecting_monitor,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_generic_200_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        detail_info = make_detail_item_with_notes_and_ticket_info()
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.open_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.return_value = (
            bruin_generic_200_response
        )
        service_affecting_monitor._should_forward_to_hnoc.return_value = False

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._unresolve_task_for_affecting_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reopen.assert_awaited_once()
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.assert_awaited_once()
        service_affecting_monitor._append_reminder_note.assert_awaited_once()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def unresolve_task_for_affecting_ticket__send_initial_reminder_email_fails_test(
        self,
        service_affecting_monitor,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_generic_200_response,
        bruin_500_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        detail_info = make_detail_item_with_notes_and_ticket_info()
        ticket_id = detail_info["ticket_overview"]["ticketID"]
        serial_number = detail_info["ticket_task"]["detailID"]
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.open_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.return_value = (
            bruin_500_response
        )
        service_affecting_monitor._should_forward_to_hnoc.return_value = False

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._unresolve_task_for_affecting_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reopen.assert_awaited_once()
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.assert_awaited_once()
        service_affecting_monitor._append_reminder_note.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def unresolve_task_for_affecting_ticket__ticket_task_reopened_test(
        self,
        service_affecting_monitor,
        make_detail_item_with_notes_and_ticket_info,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_generic_200_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        detail_info = make_detail_item_with_notes_and_ticket_info()
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.open_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._should_forward_to_hnoc.return_value = True

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._unresolve_task_for_affecting_ticket(detail_info, trouble, link_info)

        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_reopen.assert_awaited_once()
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.assert_not_awaited()
        service_affecting_monitor._should_forward_to_hnoc.assert_called()
        service_affecting_monitor._append_reminder_note.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_called_once()

    @pytest.mark.asyncio
    async def create_affecting_ticket__current_env_is_not_production_test(
        self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "dev"):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def create_affecting_ticket__create_ticket_request_has_not_2xx_status_test(
        self, service_affecting_monitor, make_structured_metrics_object_with_cache_and_contact_info, bruin_500_response
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.create_affecting_ticket.return_value = bruin_500_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def create_affecting_ticket__ticket_created_bouncing_trouble_test(
        self,
        service_affecting_monitor,
        make_structured_metrics_object_with_cache_with_events_and_contact_info,
        bruin_generic_200_response,
        make_create_ticket_200_response,
    ):
        trouble = AffectingTroubles.BOUNCING
        link_info = make_structured_metrics_object_with_cache_with_events_and_contact_info()

        service_affecting_monitor._bruin_repository.create_affecting_ticket.return_value = (
            make_create_ticket_200_response()
        )
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_awaited_once()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def create_affecting_ticket__ticket_created_dont_forward_to_hnoc_test(
        self,
        service_affecting_monitor,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_generic_200_response,
        make_create_ticket_200_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.create_affecting_ticket.return_value = (
            make_create_ticket_200_response()
        )
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.return_value = (
            bruin_generic_200_response
        )
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._should_forward_to_hnoc.return_value = False

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_awaited_once()
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.assert_awaited_once()
        service_affecting_monitor._append_reminder_note.assert_awaited_once()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def create_affecting_ticket__send_initial_reminder_email_fails_test(
        self,
        service_affecting_monitor,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_create_ticket_200_response,
        bruin_500_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.create_affecting_ticket.return_value = (
            make_create_ticket_200_response()
        )
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.return_value = (
            bruin_500_response
        )
        service_affecting_monitor._should_forward_to_hnoc.return_value = False

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_awaited_once()
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.assert_awaited_once()
        service_affecting_monitor._append_reminder_note.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()

    @pytest.mark.asyncio
    async def create_affecting_ticket__ticket_created_test(
        self,
        service_affecting_monitor,
        make_structured_metrics_object_with_cache_and_contact_info,
        bruin_generic_200_response,
        make_create_ticket_200_response,
    ):
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        link_info = make_structured_metrics_object_with_cache_and_contact_info()

        service_affecting_monitor._bruin_repository.create_affecting_ticket.return_value = (
            make_create_ticket_200_response()
        )
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response
        service_affecting_monitor._should_forward_to_hnoc.return_value = True

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._create_affecting_ticket(trouble, link_info)

        service_affecting_monitor._bruin_repository.create_affecting_ticket.assert_awaited_once()
        service_affecting_monitor._should_forward_to_hnoc.assert_called()
        service_affecting_monitor._send_reminder.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once()
        service_affecting_monitor._notifications_repository.notify_successful_ticket_creation.assert_awaited_once()
        service_affecting_monitor._bruin_repository.send_initial_email_milestone_notification.assert_not_awaited()
        service_affecting_monitor._append_reminder_note.assert_not_awaited()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_called_once()

    def should_forward_to_hnoc_non_byob_return_true_test(
        self, service_affecting_monitor, make_link, make_structured_metrics_object
    ):
        link_data = make_link(display_name="Test")
        link_metric_object = make_structured_metrics_object(link_info=link_data)
        link_label = link_metric_object["link_status"]["displayName"]

        result = service_affecting_monitor._should_forward_to_hnoc(link_label)
        assert result is True

    def should_forward_to_hnoc_byob_link_display_name_return_false_test(
        self, service_affecting_monitor, make_link, make_structured_metrics_object
    ):
        link_data = make_link(display_name="BYOB Test")
        link_metric_object = make_structured_metrics_object(link_info=link_data)
        link_label = link_metric_object["link_status"]["displayName"]

        result = service_affecting_monitor._should_forward_to_hnoc(link_label)
        assert result is False

    def schedule_forward_to_hnoc_queue_test(
        self, service_affecting_monitor, frozen_datetime, make_structured_metrics_object_with_cache_and_contact_info
    ):
        ticket_id = 12345
        serial_number = "VC1234567"
        is_byob = False
        link_type = "WIRED"
        link_info = make_structured_metrics_object_with_cache_and_contact_info()
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble
        target_queue = ForwardQueues.HNOC

        current_datetime = frozen_datetime.now()
        autoresolve_config = service_affecting_monitor._config.MONITOR_CONFIG["autoresolve"]
        wait_seconds_until_forward = autoresolve_config["last_affecting_trouble_seconds"]["day"]
        forward_time = wait_seconds_until_forward / 60
        forward_task_run_date = current_datetime + timedelta(minutes=forward_time)

        service_affecting_monitor._get_max_seconds_since_last_trouble.return_value = wait_seconds_until_forward
        service_affecting_monitor._is_link_label_blacklisted_from_hnoc.return_value = is_byob
        service_affecting_monitor._get_link_type.return_value = link_type

        with patch.multiple(service_affecting_monitor_module, datetime=frozen_datetime, timezone=Mock()):
            service_affecting_monitor._schedule_forward_to_hnoc_queue(
                forward_time=forward_time,
                ticket_id=ticket_id,
                serial_number=serial_number,
                link_data=link_info,
                trouble=trouble,
            )

        service_affecting_monitor._task_dispatcher_client.schedule_task.assert_called_once_with(
            date=forward_task_run_date,
            task_type=TaskTypes.TICKET_FORWARDS,
            task_key=f"{ticket_id}-{serial_number}-{target_queue.name}",
            task_data={
                "service": testconfig.LOG_CONFIG["name"],
                "ticket_id": ticket_id,
                "serial_number": serial_number,
                "target_queue": target_queue.value,
                "metrics_labels": {
                    "client": "",
                    "trouble": trouble.value,
                    "has_byob": is_byob,
                    "link_type": link_type,
                    "target_queue": target_queue.value,
                },
            },
        )

    @pytest.mark.asyncio
    async def run_autoresolve_process__no_metrics_found_test(
        self, service_affecting_monitor, make_list_of_link_metrics, make_rpc_response, make_contact_info
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info
        links_metrics = make_list_of_link_metrics()
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = (
            make_rpc_response(
                body=links_metrics,
                status=200,
            )
        )

        await service_affecting_monitor._run_autoresolve_process()

        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._group_links_by_edge.assert_not_called()
        service_affecting_monitor._run_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_process__empty_dataset_after_structuring_and_crossing_info_and_grouping_by_edge_test(
        self,
        service_affecting_monitor,
        make_edge,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_list_of_structured_metrics_objects,
        make_events_by_serial_and_interface,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge = make_edge(edge_state=None)  # Make it an invalid edge so crossing data produces an empty dataset
        link_with_edge_info = make_link_with_edge_info(edge_info=edge)
        link_metric_set = make_metrics_for_link(link_with_edge_info=link_with_edge_info)
        links_metric_sets = make_list_of_link_metrics(link_metric_set)

        links_structured_metrics = make_list_of_structured_metrics_objects()
        events = make_events_by_serial_and_interface()
        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info()

        service_affecting_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._run_autoresolve_process()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets, events)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_structured_metrics,
        )
        service_affecting_monitor._group_links_by_edge.assert_called_once_with(links_complete_info)
        service_affecting_monitor._run_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_process__autoresolve_triggers_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_customer_cache,
        make_edge,
        make_link,
        make_metrics,
        make_link_with_edge_info,
        make_metrics_for_link,
        make_list_of_link_metrics,
        make_structured_metrics_object_with_events,
        make_list_of_structured_metrics_objects,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_events_by_serial_and_interface,
        make_rpc_response,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"

        edge = make_edge(serial_number=edge_serial_number, edge_state="CONNECTED")
        link_1 = make_link(interface="GE1")
        edge_link_1_with_edge_info = make_link_with_edge_info(edge_info=edge, link_info=link_1)
        edge_link_1_metrics = make_metrics()
        edge_link_1_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_1_with_edge_info,
            metrics=edge_link_1_metrics,
        )
        link_2 = make_link(interface="GE2")
        edge_link_2_with_edge_info = make_link_with_edge_info(edge_info=edge, link_info=link_2)
        edge_link_2_metrics = make_metrics()
        edge_link_2_metric_set = make_metrics_for_link(
            link_with_edge_info=edge_link_2_with_edge_info,
            metrics=edge_link_2_metrics,
        )

        links_metric_sets = make_list_of_link_metrics(edge_link_1_metric_set, edge_link_2_metric_set)
        events = make_events_by_serial_and_interface(
            serials=[edge_serial_number],
            interfaces=[link_1["interface"], link_2["interface"]],
        )

        link_1_structured_metrics_object = make_structured_metrics_object_with_events(
            edge_info=edge, link_info=link_1, metrics=edge_link_1_metrics
        )
        link_2_structured_metrics_object = make_structured_metrics_object_with_events(
            edge_info=edge, link_info=link_2, metrics=edge_link_2_metrics
        )
        links_structured_metrics_objects = make_list_of_structured_metrics_objects(
            link_1_structured_metrics_object,
            link_2_structured_metrics_object,
        )

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)
        customer_cache = make_customer_cache(edge_cache_info)

        link_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=link_1_structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info,
        )
        link_2_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=link_2_structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info,
        )
        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info(
            link_1_complete_info,
            link_2_complete_info,
        )

        service_affecting_monitor._customer_cache = customer_cache
        service_affecting_monitor._velocloud_repository.get_links_metrics_for_autoresolve.return_value = (
            make_rpc_response(
                body=links_metric_sets,
                status=200,
            )
        )
        contact_info_by_client_id = {55555: [], 33333: [], 11111: [], 66666: [], 44444: [], 22222: [], 1324: []}
        service_affecting_monitor._default_contact_info_by_client_id = contact_info_by_client_id

        await service_affecting_monitor._run_autoresolve_process()

        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metric_sets, events)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            links_structured_metrics_objects,
        )
        service_affecting_monitor._group_links_by_edge.assert_called_once_with(links_complete_info)
        service_affecting_monitor._run_autoresolve_for_edge.assert_awaited_once()

    def group_links_by_edge_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_edge,
        make_link,
        make_metrics,
        make_structured_metrics_object_with_events,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_list_of_structured_metrics_objects_with_cache_and_contact_info,
        make_list_of_link_status_and_metrics_objects,
        make_link_status_and_metrics_object_with_events,
        make_links_by_edge_object,
        make_list_of_links_by_edge_objects,
        make_contact_info,
    ):
        edge_contact_info = make_contact_info()
        service_affecting_monitor._bruin_repository.get_contact_info_for_site.return_value = edge_contact_info

        edge_serial_number = "VCO123"

        edge = make_edge(serial_number=edge_serial_number)
        link_1 = make_link()
        link_2 = make_link()

        edge_link_1_metrics = make_metrics()
        edge_link_2_metrics = make_metrics()

        link_1_structured_metrics_object = make_structured_metrics_object_with_events(
            edge_info=edge, link_info=link_1, metrics=edge_link_1_metrics
        )
        link_2_structured_metrics_object = make_structured_metrics_object_with_events(
            edge_info=edge, link_info=link_2, metrics=edge_link_2_metrics
        )

        edge_cache_info = make_cached_edge(serial_number=edge_serial_number)

        link_1_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=link_1_structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info,
        )
        link_2_complete_info = make_structured_metrics_object_with_cache_and_contact_info(
            metrics_object=link_2_structured_metrics_object,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info,
        )
        links_complete_info = make_list_of_structured_metrics_objects_with_cache_and_contact_info(
            link_1_complete_info,
            link_2_complete_info,
        )

        result = service_affecting_monitor._group_links_by_edge(links_complete_info)

        link_1_status_and_metrics = make_link_status_and_metrics_object_with_events(
            link_info=link_1, metrics=edge_link_1_metrics
        )
        link_2_status_and_metrics = make_link_status_and_metrics_object_with_events(
            link_info=link_2, metrics=edge_link_2_metrics
        )
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(
            link_1_status_and_metrics, link_2_status_and_metrics
        )
        links_grouped_by_edge_obj = make_links_by_edge_object(
            edge_info=edge,
            cache_info=edge_cache_info,
            contact_info=edge_contact_info,
            links=links_status_and_metrics,
        )
        expected = make_list_of_links_by_edge_objects(links_grouped_by_edge_obj)
        assert result == expected

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__not_all_metrics_within_thresholds_test(
        self,
        service_affecting_monitor,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
    ):
        link_metrics = make_metrics(best_latency_ms_tx=9999, best_latency_ms_rx=0)
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
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
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        bruin_500_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = bruin_500_response

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__empty_list_of_tickets_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_list_of_tickets,
        make_rpc_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )

        open_affecting_tickets = make_list_of_tickets()

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__ticket_not_created_by_automation_engine_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_rpc_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by="Travis Touchdown")
        open_affecting_tickets = make_list_of_tickets(ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__get_ticket_details_request_has_not_2xx_status_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_rpc_response,
        bruin_500_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by="Intelygenz Ai")
        open_affecting_tickets = make_list_of_tickets(ticket)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = bruin_500_response

        await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__last_trouble_documented_on_ticket_creation_and_detected_long_ago_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345
        ticket_id = "432532"
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )
        ticket = make_ticket(
            ticket_id=ticket_id,
            created_by="Intelygenz Ai",
            create_date=str(CURRENT_DATETIME - timedelta(days=30)),
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
            client_id,
            service_number=serial_number,
        )

        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__last_trouble_documented_after_reopen_and_detected_long_ago_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345
        ticket_id = "432532"
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )
        ticket = make_ticket(ticket_id=ticket_id, created_by="Intelygenz Ai")
        open_affecting_tickets = make_list_of_tickets(ticket)
        detail_item = make_detail_item(value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        note_1 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nTrouble: Latency",
            service_numbers=[serial_number],
            creation_date=str(CURRENT_DATETIME - timedelta(days=30)),
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
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__maximum_number_of_autoresolves_reached_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = "432532"
        serial_number = "VC1234567"
        client_id = 12345
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )
        ticket = make_ticket(ticket_id=ticket_id, created_by="Intelygenz Ai", create_date=str(CURRENT_DATETIME))
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
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__last_trouble_documented_on_ticket_creation_and_detected_long_ago_ipa_queue_test(
        self,
        bruin_generic_200_response,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = "432532"
        serial_number = "VC1234567"
        client_id = 12345
        current_task_name = "IPA Investigate"
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )
        ticket = make_ticket(
            ticket_id=ticket_id,
            created_by="Intelygenz Ai",
            create_date=str(CURRENT_DATETIME - timedelta(days=30)),
        )
        open_affecting_tickets = make_list_of_tickets(ticket)
        detail_item = make_detail_item(id_=ticket_id, value=serial_number, current_task_name=current_task_name)
        detail_items = make_list_of_detail_items(detail_item)
        notes = make_list_of_ticket_notes()
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)
        task_type = TaskTypes.TICKET_FORWARDS
        task_key = f"{ticket_id}-{serial_number}-{ForwardQueues.HNOC.name}"

        service_affecting_monitor._get_is_byob_from_affecting_trouble_note.return_value = True
        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.return_value = bruin_generic_200_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._ticket_repository.is_ticket_task_in_ipa_queue.assert_called_with(detail_item)
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_awaited()
        service_affecting_monitor._task_dispatcher_client.clear_task.assert_called_once_with(task_type, task_key)

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__last_trouble_documented_after_reopen_and_detected_long_ago_ipa_queue_test(
        self,
        bruin_generic_200_response,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = "432532"
        serial_number = "VC1234567"
        client_id = 12345
        current_task_name = "IPA Investigate"
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )
        ticket = make_ticket(ticket_id=ticket_id, created_by="Intelygenz Ai")
        open_affecting_tickets = make_list_of_tickets(ticket)
        detail_item = make_detail_item(id_=ticket_id, value=serial_number, current_task_name=current_task_name)
        detail_items = make_list_of_detail_items(detail_item)
        note_1 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nTrouble: Latency",
            service_numbers=[serial_number],
            creation_date=str(CURRENT_DATETIME - timedelta(days=30)),
        )
        notes = make_list_of_ticket_notes(note_1)
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)
        task_type = TaskTypes.TICKET_FORWARDS
        task_key = f"{ticket_id}-{serial_number}-{ForwardQueues.HNOC.name}"

        service_affecting_monitor._get_is_byob_from_affecting_trouble_note.return_value = True
        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.return_value = bruin_generic_200_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._ticket_repository.is_ticket_task_in_ipa_queue.assert_called_with(detail_item)
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_awaited()
        service_affecting_monitor._task_dispatcher_client.clear_task.assert_called_with(task_type, task_key)

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__maximum_number_of_autoresolves_reached_in_ipa_queue_test(
        self,
        bruin_generic_200_response,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = "432532"
        serial_number = "VC1234567"
        client_id = 12345
        current_task_name = "IPA Investigate"
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )
        ticket = make_ticket(ticket_id=ticket_id, created_by="Intelygenz Ai", create_date=str(CURRENT_DATETIME))
        open_affecting_tickets = make_list_of_tickets(ticket)
        detail_item = make_detail_item(id_=ticket_id, value=serial_number, current_task_name=current_task_name)
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
        task_type = TaskTypes.TICKET_FORWARDS
        task_key = f"{ticket_id}-{serial_number}-{ForwardQueues.HNOC.name}"

        service_affecting_monitor._get_is_byob_from_affecting_trouble_note.return_value = True
        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.return_value = make_rpc_response(
            body=open_affecting_tickets,
            status=200,
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.return_value = bruin_generic_200_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._ticket_repository.is_ticket_task_in_ipa_queue.assert_called_with(detail_item)
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_awaited()
        service_affecting_monitor._task_dispatcher_client.clear_task.assert_called_with(task_type, task_key)

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__task_for_serial_already_resolved_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by="Intelygenz Ai", create_date=str(CURRENT_DATETIME))
        open_affecting_tickets = make_list_of_tickets(ticket)

        detail_item = make_detail_item(value=serial_number, status="R")
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
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__current_env_is_not_production_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )

        ticket = make_ticket(created_by="Intelygenz Ai", create_date=str(CURRENT_DATETIME))
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

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "dev"):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_not_awaited()
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__resolve_ticket_detail_request_has_not_2xx_status_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
        bruin_500_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345
        ticket_id = 123
        ticket_detail_id = 456

        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)

        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )

        ticket = make_ticket(ticket_id=ticket_id, created_by="Intelygenz Ai", create_date=str(CURRENT_DATETIME))
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

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_awaited_once_with(
            ticket_id,
            ticket_detail_id,
        )
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__ticket_task_autoresolved_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
        bruin_generic_200_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345
        ticket_id = 123
        ticket_detail_id = 456
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )
        ticket = make_ticket(ticket_id=ticket_id, created_by="Intelygenz Ai", create_date=str(CURRENT_DATETIME))
        open_affecting_tickets = make_list_of_tickets(ticket)
        detail_item = make_detail_item(id_=ticket_detail_id, value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        notes = make_list_of_ticket_notes()
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)
        task_type = TaskTypes.TICKET_FORWARDS
        task_key = f"{ticket_id}-{serial_number}-{ForwardQueues.HNOC.name}"

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

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_awaited_once_with(
            ticket_id,
            ticket_detail_id,
        )
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._task_dispatcher_client.clear_task.assert_called_with(task_type, task_key)

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge__ticket_task_autoresolved_duplicated_job_test(
        self,
        service_affecting_monitor,
        make_cached_edge,
        make_bruin_client_info,
        make_metrics,
        make_link_status_and_metrics_object_with_events,
        make_list_of_link_status_and_metrics_objects,
        make_links_by_edge_object,
        make_ticket,
        make_list_of_tickets,
        make_detail_item,
        make_list_of_detail_items,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
        bruin_generic_200_response,
    ):
        serial_number = "VC1234567"
        client_id = 12345
        ticket_id = 123
        ticket_detail_id = 456
        bruin_client_info = make_bruin_client_info(client_id=client_id)
        edge_cache_info = make_cached_edge(serial_number=serial_number, bruin_client_info=bruin_client_info)
        link_metrics = make_metrics(
            best_latency_ms_tx=0,
            best_latency_ms_rx=0,
            best_packet_loss_tx=0,
            best_packet_loss_rx=0,
            best_jitter_ms_tx=0,
            best_jitter_ms_rx=0,
            bytes_tx=1,
            bytes_rx=1,
            bps_of_best_path_tx=100,
            bps_of_best_path_rx=100,
        )
        link_status_and_metrics = make_link_status_and_metrics_object_with_events(metrics=link_metrics)
        links_status_and_metrics = make_list_of_link_status_and_metrics_objects(link_status_and_metrics)
        links_grouped_by_edge_obj = make_links_by_edge_object(
            cache_info=edge_cache_info,
            links=links_status_and_metrics,
        )
        ticket = make_ticket(ticket_id=ticket_id, created_by="Intelygenz Ai", create_date=str(CURRENT_DATETIME))
        open_affecting_tickets = make_list_of_tickets(ticket)
        detail_item = make_detail_item(id_=ticket_detail_id, value=serial_number)
        detail_items = make_list_of_detail_items(detail_item)
        notes = make_list_of_ticket_notes()
        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)
        task_type = TaskTypes.TICKET_FORWARDS
        task_key = f"{ticket_id}-{serial_number}-{ForwardQueues.HNOC.name}"

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

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._run_autoresolve_for_edge(links_grouped_by_edge_obj)

        service_affecting_monitor._bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(
            client_id,
            service_number=serial_number,
        )
        service_affecting_monitor._bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._bruin_repository.resolve_ticket.assert_awaited_once_with(
            ticket_id,
            ticket_detail_id,
        )
        service_affecting_monitor._bruin_repository.append_autoresolve_note_to_ticket.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._notifications_repository.notify_successful_autoresolve.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._task_dispatcher_client.clear_task.assert_called_with(task_type, task_key)

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_test(
        self,
        service_affecting_monitor,
        make_link,
        make_links_configuration,
        make_cached_edge,
        make_structured_metrics_object,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_detail_item,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = 12345
        serial = "VC1234567"
        task_result = "No Trouble Found - Carrier Issue"
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        link = make_link(interface="GE1")
        link_configuration = make_links_configuration(type_="WIRED", interfaces=["GE1"])

        cache_info = make_cached_edge(serial_number=serial, links_configuration=[link_configuration])
        structured_metrics_object = make_structured_metrics_object(link_info=link)
        link_data = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=cache_info, metrics_object=structured_metrics_object
        )

        detail_item = make_detail_item(value=serial)
        ticket_details = make_ticket_details(detail_items=[detail_item])

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        service_affecting_monitor._bruin_repository.change_detail_work_queue.return_value = make_rpc_response(
            body=None,
            status=200,
        )

        service_affecting_monitor._notifications_repository = Mock()
        service_affecting_monitor._notifications_repository.send_slack_message = AsyncMock()

        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._attempt_forward_to_asr(link_data, trouble, ticket_id)

        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()
        service_affecting_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        service_affecting_monitor._bruin_repository.change_detail_work_queue.assert_awaited_once_with(
            ticket_id, task_result, service_number=serial, detail_id=detail_item["detailID"]
        )
        service_affecting_monitor._bruin_repository.append_asr_forwarding_note.assert_awaited_once_with(
            ticket_id, link_data["link_status"], serial
        )
        service_affecting_monitor._notifications_repository.send_slack_message.assert_awaited_once()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_no_link_interface_found_test(
        self,
        service_affecting_monitor,
        make_link,
        make_links_configuration,
        make_cached_edge,
        make_structured_metrics_object,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_detail_item,
        make_ticket_details,
        make_rpc_response,
    ):
        forward_time = 0
        ticket_id = 12345
        serial = "VC1234567"
        task_result = "No Trouble Found - Carrier Issue"
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        link = make_link(interface="GE2")
        link_configuration = make_links_configuration(type_="WIRED", interfaces=["GE1"])

        cache_info = make_cached_edge(serial_number=serial, links_configuration=[link_configuration])
        structured_metrics_object = make_structured_metrics_object(link_info=link)
        link_data = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=cache_info, metrics_object=structured_metrics_object
        )

        detail_item = make_detail_item(value=serial)
        ticket_details = make_ticket_details(detail_items=[detail_item])

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        service_affecting_monitor._bruin_repository.change_detail_work_queue.return_value = make_rpc_response(
            body=None,
            status=200,
        )

        service_affecting_monitor._notifications_repository = Mock()
        service_affecting_monitor._notifications_repository.send_slack_message = AsyncMock()

        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._attempt_forward_to_asr(link_data, trouble, ticket_id)

        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_called_once_with(
            forward_time, ticket_id, serial, link_data, trouble
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.assert_not_awaited()
        service_affecting_monitor._bruin_repository.change_detail_work_queue.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        service_affecting_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_not_wired_test(
        self,
        service_affecting_monitor,
        make_link,
        make_links_configuration,
        make_cached_edge,
        make_structured_metrics_object,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_detail_item,
        make_ticket_details,
        make_rpc_response,
    ):
        forward_time = 0
        ticket_id = 12345
        serial = "VC1234567"
        task_result = "No Trouble Found - Carrier Issue"
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        link = make_link(interface="GE1")
        link_configuration = make_links_configuration(type_="WIRELESS", interfaces=["GE1"])

        cache_info = make_cached_edge(serial_number=serial, links_configuration=[link_configuration])
        structured_metrics_object = make_structured_metrics_object(link_info=link)
        link_data = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=cache_info, metrics_object=structured_metrics_object
        )

        detail_item = make_detail_item(value=serial)
        ticket_details = make_ticket_details(detail_items=[detail_item])

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        service_affecting_monitor._bruin_repository.change_detail_work_queue.return_value = make_rpc_response(
            body=None,
            status=200,
        )

        service_affecting_monitor._notifications_repository = Mock()
        service_affecting_monitor._notifications_repository.send_slack_message = AsyncMock()

        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._attempt_forward_to_asr(link_data, trouble, ticket_id)

        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_called_once_with(
            forward_time, ticket_id, serial, link_data, trouble
        )
        service_affecting_monitor._bruin_repository.get_ticket_details.assert_not_awaited()
        service_affecting_monitor._bruin_repository.change_detail_work_queue.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        service_affecting_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_should_not_be_forwarded_test(
        self,
        service_affecting_monitor,
        make_link,
        make_links_configuration,
        make_cached_edge,
        make_structured_metrics_object,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_detail_item,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = 12345
        serial = "VC1234567"
        task_result = "No Trouble Found - Carrier Issue"
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        link = make_link(interface="GE1", display_name="BYOB")
        link_configuration = make_links_configuration(type_="WIRED", interfaces=["GE1"])

        cache_info = make_cached_edge(serial_number=serial, links_configuration=[link_configuration])
        structured_metrics_object = make_structured_metrics_object(link_info=link)
        link_data = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=cache_info, metrics_object=structured_metrics_object
        )

        detail_item = make_detail_item(value=serial)
        ticket_details = make_ticket_details(detail_items=[detail_item])

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        service_affecting_monitor._bruin_repository.change_detail_work_queue.return_value = make_rpc_response(
            body=None,
            status=200,
        )

        service_affecting_monitor._notifications_repository = Mock()
        service_affecting_monitor._notifications_repository.send_slack_message = AsyncMock()

        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._attempt_forward_to_asr(link_data, trouble, ticket_id)

        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()
        service_affecting_monitor._bruin_repository.get_ticket_details.assert_not_awaited()
        service_affecting_monitor._bruin_repository.change_detail_work_queue.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        service_affecting_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_non_2xx_ticket_details_test(
        self,
        service_affecting_monitor,
        make_link,
        make_links_configuration,
        make_cached_edge,
        make_structured_metrics_object,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_rpc_response,
        bruin_500_response,
    ):
        ticket_id = 12345
        serial = "VC1234567"
        task_result = "No Trouble Found - Carrier Issue"
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        link = make_link(interface="GE1")
        link_configuration = make_links_configuration(type_="WIRED", interfaces=["GE1"])

        cache_info = make_cached_edge(serial_number=serial, links_configuration=[link_configuration])
        structured_metrics_object = make_structured_metrics_object(link_info=link)
        link_data = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=cache_info, metrics_object=structured_metrics_object
        )

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = bruin_500_response

        service_affecting_monitor._bruin_repository.change_detail_work_queue.return_value = make_rpc_response(
            body=None,
            status=200,
        )

        service_affecting_monitor._notifications_repository = Mock()
        service_affecting_monitor._notifications_repository.send_slack_message = AsyncMock()

        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._attempt_forward_to_asr(link_data, trouble, ticket_id)

        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()
        service_affecting_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        service_affecting_monitor._bruin_repository.change_detail_work_queue.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        service_affecting_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_other_troubles_test(
        self,
        service_affecting_monitor,
        make_link,
        make_links_configuration,
        make_cached_edge,
        make_structured_metrics_object,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_detail_item,
        make_ticket_details,
        make_rpc_response,
        make_ticket_note,
    ):
        ticket_id = 12345
        serial = "VC1234567"
        task_result = "No Trouble Found - Carrier Issue"
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        link = make_link(interface="GE1")
        link_configuration = make_links_configuration(type_="WIRED", interfaces=["GE1"])

        cache_info = make_cached_edge(serial_number=serial, links_configuration=[link_configuration])
        structured_metrics_object = make_structured_metrics_object(link_info=link)
        link_data = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=cache_info, metrics_object=structured_metrics_object
        )

        note = make_ticket_note(text=f"#*MetTel's IPA*#\nTrouble: Latency", service_numbers=[serial])
        detail_item = make_detail_item(value=serial)
        ticket_details = make_ticket_details(detail_items=[detail_item], notes=[note])

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        service_affecting_monitor._bruin_repository.change_detail_work_queue.return_value = make_rpc_response(
            body=None,
            status=200,
        )

        service_affecting_monitor._notifications_repository = Mock()
        service_affecting_monitor._notifications_repository.send_slack_message = AsyncMock()

        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._attempt_forward_to_asr(link_data, trouble, ticket_id)

        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()
        service_affecting_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        service_affecting_monitor._bruin_repository.change_detail_work_queue.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        service_affecting_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_already_forwarded_test(
        self,
        service_affecting_monitor,
        make_link,
        make_links_configuration,
        make_cached_edge,
        make_structured_metrics_object,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_detail_item,
        make_ticket_details,
        make_rpc_response,
        make_ticket_note,
    ):
        ticket_id = 12345
        serial = "VC1234567"
        task_result = "No Trouble Found - Carrier Issue"
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        link = make_link(interface="GE1")
        link_configuration = make_links_configuration(type_="WIRED", interfaces=["GE1"])

        cache_info = make_cached_edge(serial_number=serial, links_configuration=[link_configuration])
        structured_metrics_object = make_structured_metrics_object(link_info=link)
        link_data = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=cache_info, metrics_object=structured_metrics_object
        )

        note = make_ticket_note(text=f"#*MetTel's IPA*#\nMoving task to: ASR Investigate", service_numbers=[serial])
        detail_item = make_detail_item(value=serial)
        ticket_details = make_ticket_details(detail_items=[detail_item], notes=[note])

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        service_affecting_monitor._bruin_repository.change_detail_work_queue.return_value = make_rpc_response(
            body=None,
            status=200,
        )

        service_affecting_monitor._notifications_repository = Mock()
        service_affecting_monitor._notifications_repository.send_slack_message = AsyncMock()

        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._attempt_forward_to_asr(link_data, trouble, ticket_id)

        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()
        service_affecting_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        service_affecting_monitor._bruin_repository.change_detail_work_queue.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        service_affecting_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_non_2xx__change_work_queue_test(
        self,
        service_affecting_monitor,
        make_link,
        make_links_configuration,
        make_cached_edge,
        make_structured_metrics_object,
        make_structured_metrics_object_with_cache_and_contact_info,
        make_detail_item,
        make_ticket_details,
        make_rpc_response,
        bruin_500_response,
    ):
        ticket_id = 12345
        serial = "VC1234567"
        task_result = "No Trouble Found - Carrier Issue"
        trouble = AffectingTroubles.LATENCY  # We can use whatever trouble

        link = make_link(interface="GE1")
        link_configuration = make_links_configuration(type_="WIRED", interfaces=["GE1"])

        cache_info = make_cached_edge(serial_number=serial, links_configuration=[link_configuration])
        structured_metrics_object = make_structured_metrics_object(link_info=link)
        link_data = make_structured_metrics_object_with_cache_and_contact_info(
            cache_info=cache_info, metrics_object=structured_metrics_object
        )

        detail_item = make_detail_item(value=serial)
        ticket_details = make_ticket_details(detail_items=[detail_item])

        service_affecting_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        service_affecting_monitor._bruin_repository.change_detail_work_queue.return_value = bruin_500_response

        service_affecting_monitor._notifications_repository = Mock()
        service_affecting_monitor._notifications_repository.send_slack_message = AsyncMock()

        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._attempt_forward_to_asr(link_data, trouble, ticket_id)

        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_not_called()
        service_affecting_monitor._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        service_affecting_monitor._bruin_repository.change_detail_work_queue.assert_awaited_once_with(
            ticket_id, task_result, service_number=serial, detail_id=detail_item["detailID"]
        )
        service_affecting_monitor._bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        service_affecting_monitor._notifications_repository.send_slack_message.assert_not_awaited()

    def should_forward_to_asr_test(self, service_affecting_monitor, make_link, make_structured_metrics_object):
        link = make_link(display_name="Test link")
        link_data = make_structured_metrics_object(link_info=link)
        result = service_affecting_monitor._should_forward_to_asr(link_data)
        assert result is True

        link = make_link(display_name="BYOB")
        link_data = make_structured_metrics_object(link_info=link)
        result = service_affecting_monitor._should_forward_to_asr(link_data)
        assert result is False

        link = make_link(display_name="127.0.0.1")
        link_data = make_structured_metrics_object(link_info=link)
        result = service_affecting_monitor._should_forward_to_asr(link_data)
        assert result is False

    def is_link_label_blacklisted_from_asr_test(self, service_affecting_monitor):
        result = service_affecting_monitor._is_link_label_blacklisted_from_asr("Test link")
        assert result is False

        result = service_affecting_monitor._is_link_label_blacklisted_from_asr("BYOB")
        assert result is True

    def get_max_seconds_since_last_trouble_test(self, service_affecting_monitor, make_links_by_edge_object):
        edge = make_links_by_edge_object()

        day_schedule = testconfig.MONITOR_CONFIG["autoresolve"]["day_schedule"]
        last_affecting_trouble_seconds = testconfig.MONITOR_CONFIG["autoresolve"]["last_affecting_trouble_seconds"]

        current_datetime = datetime.now().replace(hour=10)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(service_affecting_monitor_module, "datetime", new=datetime_mock):
            with patch.dict(day_schedule, start_hour=6, end_hour=22):
                result = service_affecting_monitor._get_max_seconds_since_last_trouble(edge)
                assert result == last_affecting_trouble_seconds["day"]

            with patch.dict(day_schedule, start_hour=8, end_hour=0):
                result = service_affecting_monitor._get_max_seconds_since_last_trouble(edge)
                assert result == last_affecting_trouble_seconds["day"]

            with patch.dict(day_schedule, start_hour=10, end_hour=2):
                result = service_affecting_monitor._get_max_seconds_since_last_trouble(edge)
                assert result == last_affecting_trouble_seconds["day"]

            with patch.dict(day_schedule, start_hour=12, end_hour=4):
                result = service_affecting_monitor._get_max_seconds_since_last_trouble(edge)
                assert result == last_affecting_trouble_seconds["night"]

            with patch.dict(day_schedule, start_hour=2, end_hour=8):
                result = service_affecting_monitor._get_max_seconds_since_last_trouble(edge)
                assert result == last_affecting_trouble_seconds["night"]

    def was_last_reminder_sent_recently_with_previous_reminder_test(
        self, service_affecting_monitor, make_ticket_note, make_list_of_ticket_notes
    ):
        ticket_creation_date = str(CURRENT_DATETIME)
        wait_time_before_sending_new_milestone_reminder = service_affecting_monitor._config.MONITOR_CONFIG[
            "wait_time_before_sending_new_milestone_reminder"
        ]
        datetime_mock = Mock()
        note_1 = make_ticket_note(
            text="Dummy note",
            creation_date=str(CURRENT_DATETIME - timedelta(seconds=10)),
        )
        reminder_note = os.linesep.join(["#*MetTel's IPA*#", "Client Reminder"])
        note_2 = make_ticket_note(
            text=reminder_note,
            creation_date=str(CURRENT_DATETIME + timedelta(hours=42)),
        )
        notes = make_list_of_ticket_notes(note_1, note_2)

        now = CURRENT_DATETIME + timedelta(hours=42)
        datetime_mock.now = Mock(return_value=now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = service_affecting_monitor._was_last_reminder_sent_recently(
                notes, ticket_creation_date, wait_time_before_sending_new_milestone_reminder
            )

            assert result is True

        ticket_creation_date = str(CURRENT_DATETIME + timedelta(hours=54))
        now = CURRENT_DATETIME + timedelta(hours=54)
        datetime_mock.now = Mock(return_value=now)
        note_2 = make_ticket_note(
            text=reminder_note,
            creation_date=str(CURRENT_DATETIME - timedelta(hours=24)),
        )
        notes = make_list_of_ticket_notes(note_1, note_2)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = service_affecting_monitor._was_last_reminder_sent_recently(
                notes, ticket_creation_date, wait_time_before_sending_new_milestone_reminder
            )

            assert result is False

        service_affecting_monitor._utils_repository.has_last_event_happened_recently.assert_called_with(
            notes, ticket_creation_date, max_seconds_since_last_event=86400.0, regex=REMINDER_NOTE_REGEX
        )

    def was_last_reminder_sent_recently_without_previous_reminder_test(
        self, service_affecting_monitor, make_ticket_note, make_list_of_ticket_notes
    ):
        ticket_creation_date = str(CURRENT_DATETIME)
        wait_time_before_sending_new_milestone_reminder = service_affecting_monitor._config.MONITOR_CONFIG[
            "wait_time_before_sending_new_milestone_reminder"
        ]
        datetime_mock = Mock()
        note_1 = make_ticket_note(
            text="Dummy note",
            creation_date=str(CURRENT_DATETIME - timedelta(seconds=10)),
        )
        note_2 = make_ticket_note(
            text="This email is not a reminder",
            creation_date=str(CURRENT_DATETIME),
        )
        notes = make_list_of_ticket_notes(note_1, note_2)

        datetime_mock.now = Mock(return_value=CURRENT_DATETIME)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = service_affecting_monitor._was_last_reminder_sent_recently(
                notes, ticket_creation_date, wait_time_before_sending_new_milestone_reminder
            )

            assert result is True

        now = CURRENT_DATETIME + timedelta(hours=42)
        datetime_mock.now = Mock(return_value=now)
        with patch.object(utils_repository_module, "datetime", new=datetime_mock):
            result = service_affecting_monitor._was_last_reminder_sent_recently(
                notes, ticket_creation_date, wait_time_before_sending_new_milestone_reminder
            )

            assert result is False

        service_affecting_monitor._utils_repository.has_last_event_happened_recently.assert_called_with(
            notes, ticket_creation_date, max_seconds_since_last_event=86400.0, regex=REMINDER_NOTE_REGEX
        )

    @pytest.mark.asyncio
    async def send_reminder__last_trouble_documented_on_ticket_creation_and_detected_one_day_ago_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
        bruin_generic_200_response,
    ):
        serial_number = "VC1234567"
        ticket = make_ticket(
            created_by="Intelygenz Ai",
            create_date=str(CURRENT_DATETIME - timedelta(hours=24)),
        )
        ticket_id = ticket["ticketID"]
        last_documentation_cycle_start_date = ticket["createDate"]
        detail_item = make_detail_item(status="I", value=serial_number)
        detail_object = make_detail_item_with_notes_and_ticket_info(
            detail_item=detail_item,
            ticket_info=ticket,
        )
        wait_time_before_sending_new_milestone_reminder = service_affecting_monitor._config.MONITOR_CONFIG[
            "wait_time_before_sending_new_milestone_reminder"
        ]
        reminder_note = os.linesep.join(["#*MetTel's IPA*#", "Client Reminder"])
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        service_affecting_monitor._bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._send_reminder(detail_object)

        service_affecting_monitor._was_last_reminder_sent_recently.assert_called_once_with(
            [], last_documentation_cycle_start_date, wait_time_before_sending_new_milestone_reminder
        )
        service_affecting_monitor._bruin_repository.send_reminder_email_milestone_notification.assert_awaited_once_with(
            ticket_id, serial_number
        )
        service_affecting_monitor._append_reminder_note.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id,
            reminder_note,
            service_numbers=[serial_number],
        )
        service_affecting_monitor._notifications_repository.notify_successful_reminder_note_append.assert_awaited_with(
            ticket_id, serial_number
        )

    @pytest.mark.asyncio
    async def send_reminder__creation_date_less_than_24_hours_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
    ):
        serial_number = "VC1234567"
        ticket = make_ticket(
            created_by="Intelygenz Ai",
            create_date=str(CURRENT_DATETIME - timedelta(hours=1)),
        )
        ticket_id = ticket["ticketID"]
        last_documentation_cycle_start_date = ticket["createDate"]
        detail_item = make_detail_item(status="I", value=serial_number)
        detail_object = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, ticket_info=ticket)
        wait_time_before_sending_new_milestone_reminder = service_affecting_monitor._config.MONITOR_CONFIG[
            "wait_time_before_sending_new_milestone_reminder"
        ]

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._send_reminder(detail_object)

        service_affecting_monitor._was_last_reminder_sent_recently.assert_called_once_with(
            [], last_documentation_cycle_start_date, wait_time_before_sending_new_milestone_reminder
        )
        service_affecting_monitor._bruin_repository.send_reminder_email_milestone_notification.assert_not_awaited()
        service_affecting_monitor._append_reminder_note.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reminder_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_reminder__last_note_less_than_24_hours_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
        make_ticket_note,
    ):
        serial_number = "VC1234567"
        ticket = make_ticket(
            created_by="Intelygenz Ai",
            create_date=str(CURRENT_DATETIME - timedelta(hours=48)),
        )
        reminder_note = os.linesep.join(["#*MetTel's IPA*#", "Client Reminder"])
        last_note_date = str(CURRENT_DATETIME)
        note = make_ticket_note(
            text=reminder_note,
            creation_date=last_note_date,
        )
        ticket_id = ticket["ticketID"]
        last_documentation_cycle_start_date = last_note_date
        detail_item = make_detail_item(status="I", value=serial_number)
        detail_object = make_detail_item_with_notes_and_ticket_info(
            detail_item=detail_item, ticket_info=ticket, notes=[note]
        )
        wait_time_before_sending_new_milestone_reminder = service_affecting_monitor._config.MONITOR_CONFIG[
            "wait_time_before_sending_new_milestone_reminder"
        ]

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._send_reminder(detail_object)

        service_affecting_monitor._was_last_reminder_sent_recently.assert_called_once_with(
            [note], last_documentation_cycle_start_date, wait_time_before_sending_new_milestone_reminder
        )
        service_affecting_monitor._bruin_repository.send_reminder_email_milestone_notification.assert_not_awaited()
        service_affecting_monitor._append_reminder_note.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reminder_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_reminder__failed_to_send_email_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
        bruin_generic_200_response,
        bruin_500_response,
    ):
        serial_number = "VC1234567"
        ticket = make_ticket(
            created_by="Intelygenz Ai",
            create_date=str(CURRENT_DATETIME - timedelta(hours=48)),
        )
        ticket_id = ticket["ticketID"]
        last_documentation_cycle_start_date = ticket["createDate"]
        detail_item = make_detail_item(status="I", value=serial_number)
        detail_object = make_detail_item_with_notes_and_ticket_info(
            detail_item=detail_item,
            ticket_info=ticket,
        )
        wait_time_before_sending_new_milestone_reminder = service_affecting_monitor._config.MONITOR_CONFIG[
            "wait_time_before_sending_new_milestone_reminder"
        ]
        service_affecting_monitor._bruin_repository._nats_client.request.return_value = bruin_generic_200_response
        service_affecting_monitor._bruin_repository.send_reminder_email_milestone_notification.return_value = (
            bruin_500_response
        )

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._send_reminder(detail_object)

        service_affecting_monitor._was_last_reminder_sent_recently.assert_called_once_with(
            [], last_documentation_cycle_start_date, wait_time_before_sending_new_milestone_reminder
        )
        service_affecting_monitor._bruin_repository.send_reminder_email_milestone_notification.assert_awaited_once_with(
            ticket_id, serial_number
        )
        service_affecting_monitor._append_reminder_note.assert_not_awaited()
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notifications_repository.notify_successful_reminder_note_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_reminder__failed_to_append_note_test(
        self,
        service_affecting_monitor,
        make_ticket,
        make_detail_item,
        make_detail_item_with_notes_and_ticket_info,
        bruin_generic_200_response,
        bruin_500_response,
    ):
        serial_number = "VC1234567"
        ticket = make_ticket(
            created_by="Intelygenz Ai",
            create_date=str(CURRENT_DATETIME - timedelta(hours=48)),
        )
        ticket_id = ticket["ticketID"]
        last_documentation_cycle_start_date = ticket["createDate"]
        detail_item = make_detail_item(status="I", value=serial_number)
        detail_object = make_detail_item_with_notes_and_ticket_info(
            detail_item=detail_item,
            ticket_info=ticket,
        )
        reminder_note = os.linesep.join(["#*MetTel's IPA*#", "Client Reminder"])
        wait_time_before_sending_new_milestone_reminder = service_affecting_monitor._config.MONITOR_CONFIG[
            "wait_time_before_sending_new_milestone_reminder"
        ]
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        service_affecting_monitor._bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        service_affecting_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_500_response

        with patch.object(service_affecting_monitor._config, "CURRENT_ENVIRONMENT", "production"):
            await service_affecting_monitor._send_reminder(detail_object)

        service_affecting_monitor._was_last_reminder_sent_recently.assert_called_once_with(
            [], last_documentation_cycle_start_date, wait_time_before_sending_new_milestone_reminder
        )
        service_affecting_monitor._bruin_repository.send_reminder_email_milestone_notification.assert_awaited_once_with(
            ticket_id, serial_number
        )
        service_affecting_monitor._append_reminder_note.assert_awaited_once_with(
            ticket_id,
            serial_number,
        )
        service_affecting_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id,
            reminder_note,
            service_numbers=[serial_number],
        )
        service_affecting_monitor._notifications_repository.notify_successful_reminder_note_append.assert_not_awaited()

    def get_default_contact_info_by_client_id_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_edge_full_id,
        make_cached_edge,
        make_customer_cache,
    ):
        contact_info_by_host_and_client_id = testconfig.MONITOR_CONFIG["contact_info_by_host_and_client_id"]

        host_1 = "host-1"
        host_2 = "host-2"
        host_3 = "host-3"

        client_id_1 = 1
        client_id_2 = 2
        client_id_3 = 3
        client_id_4 = 4
        client_id_5 = 5
        client_id_6 = 6

        bruin_client_info_1 = make_bruin_client_info(client_id=client_id_1)
        bruin_client_info_2 = make_bruin_client_info(client_id=client_id_2)
        bruin_client_info_3 = make_bruin_client_info(client_id=client_id_3)
        bruin_client_info_4 = make_bruin_client_info(client_id=client_id_4)
        bruin_client_info_5 = make_bruin_client_info(client_id=client_id_5)
        bruin_client_info_6 = make_bruin_client_info(client_id=client_id_6)

        full_id_1 = make_edge_full_id(host=host_1)
        full_id_2 = make_edge_full_id(host=host_2)
        full_id_3 = make_edge_full_id(host=host_3)

        edge_1 = make_cached_edge(full_id=full_id_1, bruin_client_info=bruin_client_info_1)
        edge_2 = make_cached_edge(full_id=full_id_1, bruin_client_info=bruin_client_info_2)
        edge_3 = make_cached_edge(full_id=full_id_2, bruin_client_info=bruin_client_info_3)
        edge_4 = make_cached_edge(full_id=full_id_2, bruin_client_info=bruin_client_info_4)
        edge_5 = make_cached_edge(full_id=full_id_3, bruin_client_info=bruin_client_info_5)
        edge_6 = make_cached_edge(full_id=full_id_3, bruin_client_info=bruin_client_info_6)

        customer_cache = make_customer_cache(edge_1, edge_2, edge_3, edge_4, edge_5, edge_6)
        service_affecting_monitor._customer_cache = customer_cache

        result = service_affecting_monitor._get_default_contact_info_by_client_id()

        assert result == {
            client_id_1: contact_info_by_host_and_client_id[host_1][client_id_1],
            client_id_2: contact_info_by_host_and_client_id[host_1][client_id_2],
            client_id_3: contact_info_by_host_and_client_id[host_2]["*"],
            client_id_4: contact_info_by_host_and_client_id[host_2]["*"],
            client_id_5: contact_info_by_host_and_client_id[host_3]["*"],
            client_id_6: contact_info_by_host_and_client_id[host_3]["*"],
        }

    def should_use_default_contact_info_test(
        self,
        service_affecting_monitor,
        make_bruin_client_info,
        make_edge_full_id,
        make_cached_edge,
    ):
        client_id_1 = 1
        client_id_2 = 2
        client_id_3 = 3

        bruin_client_info_1 = make_bruin_client_info(client_id=client_id_1)
        bruin_client_info_2 = make_bruin_client_info(client_id=client_id_2)
        bruin_client_info_3 = make_bruin_client_info(client_id=client_id_3)

        full_id_1 = make_edge_full_id(host="host-2")

        edge_1 = make_cached_edge(bruin_client_info=bruin_client_info_1)
        edge_2 = make_cached_edge(bruin_client_info=bruin_client_info_2, full_id=full_id_1)
        edge_3 = make_cached_edge(bruin_client_info=bruin_client_info_3)

        result = service_affecting_monitor._should_use_default_contact_info(client_id_1, edge_1)
        assert result is True

        result = service_affecting_monitor._should_use_default_contact_info(client_id_2, edge_2)
        assert result is True

        result = service_affecting_monitor._should_use_default_contact_info(client_id_3, edge_3)
        assert result is False
