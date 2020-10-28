from unittest.mock import call
from collections import OrderedDict
from datetime import datetime, timedelta
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch
from shortuuid import uuid

import json
import pytest

from application.actions import service_affecting_monitor as service_affecting_monitor_module
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from apscheduler.util import undefined
from asynctest import CoroutineMock

from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(service_affecting_monitor_module, 'uuid', return_value=uuid_)


class TestServiceAffectingMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)

        assert service_affecting_monitor._event_bus is event_bus
        assert service_affecting_monitor._logger is logger
        assert service_affecting_monitor._scheduler is scheduler
        assert service_affecting_monitor._config is config
        assert service_affecting_monitor._metrics_repository is metrics_repository
        assert service_affecting_monitor._bruin_repository is bruin_repository
        assert service_affecting_monitor._velocloud_repository is velocloud_repository
        assert service_affecting_monitor._customer_cache_repository is customer_cache_repository

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(service_affecting_monitor_module, 'timezone', new=Mock()):
                await service_affecting_monitor.start_service_affecting_monitor_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._service_affecting_monitor_process, 'interval',
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=next_run_time,
            replace_existing=True,
            id='_monitor_each_edge',
        )

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        await service_affecting_monitor.start_service_affecting_monitor_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._service_affecting_monitor_process, 'interval',
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=undefined,
            replace_existing=True,
            id='_monitor_each_edge',
        )

    @pytest.mark.asyncio
    async def service_affecting_monitor_process_ok_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        metrics_repository = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()

        customer_cache_list = ['edges']
        customer_cache_return = {
                                    "body": customer_cache_list,
                                    "status": 200
                                }
        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=customer_cache_return)

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._latency_check = CoroutineMock()
        service_affecting_monitor._packet_loss_check = CoroutineMock()
        service_affecting_monitor._jitter_check = CoroutineMock()

        await service_affecting_monitor._service_affecting_monitor_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_awaited_once()
        service_affecting_monitor._packet_loss_check.assert_awaited_once()
        service_affecting_monitor._jitter_check.assert_awaited_once()

    @pytest.mark.asyncio
    async def service_affecting_monitor_process_non_2xx_customer_cache_return_ko_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        metrics_repository = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()

        customer_cache_list = ['edges']
        customer_cache_return = {
            "body": customer_cache_list,
            "status": 500
        }
        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=customer_cache_return)

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._latency_check = CoroutineMock()
        service_affecting_monitor._packet_loss_check = CoroutineMock()
        service_affecting_monitor._jitter_check = CoroutineMock()

        await service_affecting_monitor._service_affecting_monitor_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_not_awaited()
        service_affecting_monitor._packet_loss_check.assert_not_awaited()
        service_affecting_monitor._jitter_check.assert_not_awaited()

    @pytest.mark.asyncio
    async def service_affecting_monitor_process_empty_customer_cache_return_ko_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        metrics_repository = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()

        customer_cache_list = []
        customer_cache_return = {
            "body": customer_cache_list,
            "status": 200
        }
        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=customer_cache_return)

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._latency_check = CoroutineMock()
        service_affecting_monitor._packet_loss_check = CoroutineMock()
        service_affecting_monitor._jitter_check = CoroutineMock()

        await service_affecting_monitor._service_affecting_monitor_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_not_awaited()
        service_affecting_monitor._packet_loss_check.assert_not_awaited()
        service_affecting_monitor._jitter_check.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check_with_no_troubles_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_best_latency_ms_rx = 14
        link_1_best_latency_ms_tx = 115
        link_2_best_latency_ms_rx = 40
        link_2_best_latency_ms_tx = 20
        link_3_best_latency_ms_rx = 30
        link_3_best_latency_ms_tx = 30

        link_1 = {
            'bestLatencyMsRx': link_1_best_latency_ms_rx,
            'bestLatencyMsTx': link_1_best_latency_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }
        link_2 = {
            'bestLatencyMsRx': link_2_best_latency_ms_rx,
            'bestLatencyMsTx': link_2_best_latency_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }
        link_3 = {
            'bestLatencyMsRx': link_3_best_latency_ms_rx,
            'bestLatencyMsTx': link_3_best_latency_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }

        links_metric_body = [link_1, link_2, link_3]
        links_metric_status = 200

        link_metrics_return = {
                                'body': links_metric_body,
                                'status': links_metric_status

        }

        structure_link_1 = {
                            'edge_status': {
                                            "host": "mettel.velocloud.net",
                                            "enterprise_id": 137,
                                            "edge_id": 1602,
                                            "name": "TEST",
                                            "edgeState": "OFFLINE",
                                            "serialNumber": "VC05200028729",
                                            "enterprise_name": "Titan America|85940|"},
                            'link_status': {
                                            'interface': 'GE1'
                            },
                            'link_metrics': {
                                'bestLatencyMsRx': link_1_best_latency_ms_rx,
                                'bestLatencyMsTx': link_1_best_latency_ms_tx,
                            }
        }
        structure_link_2 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE2'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_2_best_latency_ms_rx,
                'bestLatencyMsTx': link_2_best_latency_ms_tx,
            }
        }
        structure_link_3 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE3'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_3_best_latency_ms_rx,
                'bestLatencyMsTx': link_3_best_latency_ms_tx,
            }
        }
        structure_link_return = [structure_link_1,
                                 structure_link_2,
                                 structure_link_3]
        metrics_with_cache_and_contact_info_return = [
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_1},
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_2},
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_3}]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_latency_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)
        service_affecting_monitor._compose_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check()

        velocloud_repository.get_links_metrics_for_latency_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check_empty_link_metrics_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        links_metric_body = []
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_latency_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock()
        service_affecting_monitor._compose_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check()

        velocloud_repository.get_links_metrics_for_latency_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._compose_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check_with_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_latency_ms_rx = 14
        link_best_latency_ms_tx = 121

        link_1 = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }

        links_metric_body = [link_1]
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }

        structure_link_1 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_best_latency_ms_rx,
                'bestLatencyMsTx': link_best_latency_ms_tx,
            }
        }

        structure_link_return = [structure_link_1]
        metrics_with_cache_and_contact_info_return = [
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_1}]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_latency_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)

        ticket_dict = {'ticket': 'some ticket details'}
        service_affecting_monitor._compose_ticket_dict = Mock(return_value=ticket_dict)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check()

        velocloud_repository.get_links_metrics_for_latency_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_ticket_dict.assert_called_once_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            input=link_best_latency_ms_rx,
            output=link_best_latency_ms_tx,
            trouble='Latency',
            threshold=config.MONITOR_CONFIG["latency"]
        )
        service_affecting_monitor._notify_trouble.assert_awaited_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            trouble='Latency',
            ticket_dict=ticket_dict
        )

    @pytest.mark.asyncio
    async def latency_check_with_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_latency_ms_rx = 121
        link_best_latency_ms_tx = 14

        link_1 = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }

        links_metric_body = [link_1]
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }

        structure_link_1 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_best_latency_ms_rx,
                'bestLatencyMsTx': link_best_latency_ms_tx,
            }
        }

        structure_link_return = [structure_link_1]
        metrics_with_cache_and_contact_info_return = [
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_1}]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_latency_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)

        ticket_dict = {'ticket': 'some ticket details'}
        service_affecting_monitor._compose_ticket_dict = Mock(return_value=ticket_dict)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check()

        velocloud_repository.get_links_metrics_for_latency_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_ticket_dict.assert_called_once_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            input=link_best_latency_ms_rx,
            output=link_best_latency_ms_tx,
            trouble='Latency',
            threshold=config.MONITOR_CONFIG["latency"]
        )
        service_affecting_monitor._notify_trouble.assert_awaited_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            trouble='Latency',
            ticket_dict=ticket_dict
        )

    @pytest.mark.asyncio
    async def packet_loss_check_with_no_troubles_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_best_loss_packets_rx = 6
        link_1_best_loss_packets_tx = 7
        link_2_best_loss_packets_rx = 1
        link_2_best_loss_packets_tx = 2
        link_3_best_loss_packets_rx = 3
        link_3_best_loss_packets_tx = 4

        link_1 = {
            'bestLossPctRx': link_1_best_loss_packets_rx,
            'bestLossPctTx': link_1_best_loss_packets_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }
        link_2 = {
            'bestLossPctRx': link_2_best_loss_packets_rx,
            'bestLossPctTx': link_2_best_loss_packets_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }
        link_3 = {
            'bestLossPctRx': link_3_best_loss_packets_rx,
            'bestLossPctTx': link_3_best_loss_packets_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }

        links_metric_body = [link_1, link_2, link_3]
        links_metric_status = 200

        link_metrics_return = {
                                'body': links_metric_body,
                                'status': links_metric_status

        }

        structure_link_1 = {
                            'edge_status': {
                                            "host": "mettel.velocloud.net",
                                            "enterprise_id": 137,
                                            "edge_id": 1602,
                                            "name": "TEST",
                                            "edgeState": "OFFLINE",
                                            "serialNumber": "VC05200028729",
                                            "enterprise_name": "Titan America|85940|"},
                            'link_status': {
                                            'interface': 'GE1'
                            },
                            'link_metrics': {
                                'bestLossPctRx': link_1_best_loss_packets_rx,
                                'bestLossPctTx': link_1_best_loss_packets_tx,
                            }
        }
        structure_link_2 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE2'
            },
            'link_metrics': {
                'bestLossPctRx': link_2_best_loss_packets_rx,
                'bestLossPctTx': link_2_best_loss_packets_tx,
            }
        }
        structure_link_3 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE3'
            },
            'link_metrics': {
                'bestLossPctRx': link_3_best_loss_packets_rx,
                'bestLossPctTx': link_3_best_loss_packets_tx,
            }
        }
        structure_link_return = [structure_link_1,
                                 structure_link_2,
                                 structure_link_3]
        metrics_with_cache_and_contact_info_return = [
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_1},
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_2},
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_3}]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_packet_loss_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)
        service_affecting_monitor._compose_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check()

        velocloud_repository.get_links_metrics_for_packet_loss_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check_empty_link_metrics_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        links_metric_body = []
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_packet_loss_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock()
        service_affecting_monitor._compose_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check()

        velocloud_repository.get_links_metrics_for_packet_loss_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._compose_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_loss_packets_rx = 7
        link_best_loss_packets_tx = 10

        link_1 = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }

        links_metric_body = [link_1]
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }

        structure_link_1 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLossPctRx': link_best_loss_packets_rx,
                'bestLossPctTx': link_best_loss_packets_tx,
            }
        }

        structure_link_return = [structure_link_1]
        metrics_with_cache_and_contact_info_return = [
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_1}]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_packet_loss_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)

        ticket_dict = {'ticket': 'some ticket details'}
        service_affecting_monitor._compose_ticket_dict = Mock(return_value=ticket_dict)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check()

        velocloud_repository.get_links_metrics_for_packet_loss_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_ticket_dict.assert_called_once_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            input=link_best_loss_packets_rx,
            output=link_best_loss_packets_tx,
            trouble='Packet Loss',
            threshold=config.MONITOR_CONFIG["packet_loss"]
        )
        service_affecting_monitor._notify_trouble.assert_awaited_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            trouble='Packet Loss',
            ticket_dict=ticket_dict
        )

    @pytest.mark.asyncio
    async def packet_loss_check_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_loss_packets_rx = 10
        link_best_loss_packets_tx = 7

        link_1 = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }

        links_metric_body = [link_1]
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }

        structure_link_1 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLossPctRx': link_best_loss_packets_rx,
                'bestLossPctTx': link_best_loss_packets_tx,
            }
        }

        structure_link_return = [structure_link_1]
        metrics_with_cache_and_contact_info_return = [
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_1}, ]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_packet_loss_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)

        ticket_dict = {'ticket': 'some ticket details'}
        service_affecting_monitor._compose_ticket_dict = Mock(return_value=ticket_dict)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check()

        velocloud_repository.get_links_metrics_for_packet_loss_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_ticket_dict.assert_called_once_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            input=link_best_loss_packets_rx,
            output=link_best_loss_packets_tx,
            trouble='Packet Loss',
            threshold=config.MONITOR_CONFIG["packet_loss"]
        )
        service_affecting_monitor._notify_trouble.assert_awaited_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            trouble='Packet Loss',
            ticket_dict=ticket_dict
        )

    @pytest.mark.asyncio
    async def jitter_check_with_below_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_best_jitter_ms_rx = 14
        link_1_best_jitter_ms_tx = 15
        link_2_best_jitter_ms_rx = 10
        link_2_best_jitter_ms_tx = 20

        link_1 = {
            'bestJitterMsRx': link_1_best_jitter_ms_rx,
            'bestJitterMsTx': link_1_best_jitter_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }
        link_2 = {
            'bestJitterMsRx': link_2_best_jitter_ms_rx,
            'bestJitterMsTx': link_2_best_jitter_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }

        links_metric_body = [link_1, link_2]
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }

        structure_link_1 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestJitterMsRx': link_1_best_jitter_ms_rx,
                'bestJitterMsTx': link_1_best_jitter_ms_tx,
            }
        }
        structure_link_2 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE2'
            },
            'link_metrics': {
                'bestJitterMsRx': link_2_best_jitter_ms_rx,
                'bestJitterMsTx': link_2_best_jitter_ms_tx,
            }
        }

        structure_link_return = [structure_link_1,
                                 structure_link_2]
        metrics_with_cache_and_contact_info_return = [
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_1},
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_2}]
        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_jitter_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)
        service_affecting_monitor._compose_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._jitter_check()

        velocloud_repository.get_links_metrics_for_jitter_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def jitter_check_empty_link_metrics_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        links_metric_body = []
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }
        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_jitter_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock()
        service_affecting_monitor._compose_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._jitter_check()

        velocloud_repository.get_links_metrics_for_jitter_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._compose_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def jitter_check_with_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_best_jitter_ms_rx = 32
        link_1_best_jitter_ms_tx = 15
        link_2_best_jitter_ms_rx = 10
        link_2_best_jitter_ms_tx = 20

        link_1 = {
            'bestJitterMsRx': link_1_best_jitter_ms_rx,
            'bestJitterMsTx': link_1_best_jitter_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }
        link_2 = {
            'bestJitterMsRx': link_2_best_jitter_ms_rx,
            'bestJitterMsTx': link_2_best_jitter_ms_tx,
            'link': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|",

            }
        }

        links_metric_body = [link_1, link_2]
        links_metric_status = 200

        link_metrics_return = {
            'body': links_metric_body,
            'status': links_metric_status

        }

        structure_link_1 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestJitterMsRx': link_1_best_jitter_ms_rx,
                'bestJitterMsTx': link_1_best_jitter_ms_tx,
            }
        }
        structure_link_2 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE2'
            },
            'link_metrics': {
                'bestJitterMsRx': link_2_best_jitter_ms_rx,
                'bestJitterMsTx': link_2_best_jitter_ms_tx,
            }
        }

        structure_link_return = [structure_link_1,
                                 structure_link_2]
        metrics_with_cache_and_contact_info_return = [
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_1},
            {'cached_info': {'edge': device}, 'contact_info': "some_contact_info", **structure_link_2}]
        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_jitter_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)
        ticket_dict = {'ticket': 'some ticket details'}
        service_affecting_monitor._compose_ticket_dict = Mock(return_value=ticket_dict)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._jitter_check()

        velocloud_repository.get_links_metrics_for_jitter_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_ticket_dict.assert_called_once_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            input=link_1_best_jitter_ms_rx,
            output=link_1_best_jitter_ms_tx,
            trouble='Jitter',
            threshold=config.MONITOR_CONFIG["jitter"],

        )
        service_affecting_monitor._notify_trouble.assert_awaited_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            trouble='Jitter',
            ticket_dict=ticket_dict
        )

    @pytest.mark.asyncio
    async def notify_trouble_with_ticket_already_existing_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                                "ticket": {
                                    "email": "fake@gmail.com",
                                    "phone": "111-111-1111",
                                    "name": "Fake Guy",
                                },
                                "site": {
                                    "email": "fake@gmail.com",
                                    "phone": "111-111-1111",
                                    "name": "Fake Guy",
                                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config["environment"] = 'production'
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "R"}],
            "ticketNotes": [
                {
                    "noteValue": '#*Automation Engine*# \n '
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        open_ticket_response_mock = {
            'status': 200,
            'body': {}
        }
        client_id = 85940
        slack_message_mock = (
            f'Affecting ticket {ticket_mock["ticketID"]} reopened. Details at '
            f'https://app.bruin.com/t/{ticket_mock["ticketID"]}'
        )
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._ticket_object_to_string_without_watermark = Mock()
        service_affecting_monitor._bruin_repository.open_ticket = CoroutineMock(side_effect=[open_ticket_response_mock])
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._ticket_object_to_string_without_watermark.assert_called_once()
        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once_with(
            ticket_mock['ticketID'], ticket_mock['ticketDetails'][0]['detailID'])
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message.\
            assert_awaited_once_with(slack_message_mock)
        service_affecting_monitor._metrics_repository.increment_tickets_reopened.assert_called_once()

    @pytest.mark.asyncio
    async def notify_trouble_with_ticket_already_existing_no_details_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                                "ticket": {
                                    "email": "fake@gmail.com",
                                    "phone": "111-111-1111",
                                    "name": "Fake Guy",
                                },
                                "site": {
                                    "email": "fake@gmail.com",
                                    "phone": "111-111-1111",
                                    "name": "Fake Guy",
                                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config["environment"] = 'production'
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": '', "detailStatus": "R"}],
            "ticketNotes": [
                {
                    "noteValue": '#*Automation Engine*# \n '
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        open_ticket_response_mock = {
            'status': 200,
            'body': {}
        }

        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._ticket_object_to_string_without_watermark = Mock()
        service_affecting_monitor._bruin_repository.open_ticket = CoroutineMock(side_effect=[open_ticket_response_mock])
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._ticket_object_to_string_without_watermark.assert_not_called()
        service_affecting_monitor._bruin_repository.open_ticket.assert_not_awaited()
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message.\
            assert_not_awaited()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened.assert_not_called()

    @pytest.mark.asyncio
    async def notify_trouble_with_open_different_trouble_ticket_already_existing_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config["environment"] = 'production'
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "O"}],
            "ticketNotes": [
                {
                    "noteValue": '#*Automation Engine*# \n '
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        open_ticket_response_mock = {
            'status': 200,
            'body': {}
        }
        slack_message = f'Posting JITTER note to ticket id: 3521039\n' \
                        f'https://app.bruin.com/helpdesk?clientId=85940&'\
                        f'ticketId=3521039 , in '\
                        f'production'
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._ticket_object_to_string_without_watermark = Mock()
        service_affecting_monitor._bruin_repository.open_ticket = CoroutineMock(side_effect=[open_ticket_response_mock])
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._notify_trouble(link_info, 'JITTER', ticket_dict)

        bruin_repository.append_note_to_ticket.assert_awaited_once()
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        service_affecting_monitor._ticket_object_to_string_without_watermark.assert_not_called()
        service_affecting_monitor._bruin_repository.open_ticket.assert_not_awaited()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened.assert_not_called()

    @pytest.mark.asyncio
    async def notify_trouble_with_open_same_trouble_ticket_already_existing_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config["environment"] = 'production'
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "O"}],
            "ticketNotes": [
                {
                    "noteValue": '#*Automation Engine*# \n '
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        open_ticket_response_mock = {
            'status': 200,
            'body': {}
        }

        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._ticket_object_to_string_without_watermark = Mock()
        service_affecting_monitor._bruin_repository.open_ticket = CoroutineMock(side_effect=[open_ticket_response_mock])
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        bruin_repository.append_note_to_ticket.assert_not_awaited()
        bruin_repository._notifications_repository.send_slack_message.assert_not_awaited()
        service_affecting_monitor._ticket_object_to_string_without_watermark.assert_not_called()
        service_affecting_monitor._bruin_repository.open_ticket.assert_not_awaited()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened.assert_not_called()

    @pytest.mark.asyncio
    async def notify_trouble_with_ticket_already_existing_with_error_open_ticket_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()

        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}
        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config["environment"] = 'production'
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "R"}],
            "ticketNotes": [
                {
                    "noteValue": '#*Automation Engine*# \n '
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        open_ticket_response_mock = {
            'status': 400,
            'body': {}
        }
        client_id = 85940
        err_message_mock = (
            f'[service-affecting-monitor] Error: Could not reopen ticket: {ticket_mock}'
        )
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._ticket_object_to_string = Mock()
        service_affecting_monitor._bruin_repository.open_ticket = CoroutineMock(side_effect=[open_ticket_response_mock])
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._ticket_object_to_string.assert_not_called()
        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once_with(
            ticket_mock['ticketID'], ticket_mock['ticketDetails'][0]['detailID'])
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message. \
            assert_awaited_once_with(err_message_mock)

    @pytest.mark.asyncio
    async def notify_trouble_with_no_existing_ticket_and_dev_environment_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()

        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_mock = None
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._ticket_object_to_string = Mock()

        await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._ticket_object_to_string.assert_not_called()

    @pytest.mark.asyncio
    async def notify_trouble_with_no_existing_ticket_and_production_environment_failed_rpc_test(self):
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        metrics_repository.increment_tickets_created = Mock()
        bruin_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[{'body': 'Failed', 'status': 400},
                                                           'Note Posted',
                                                           'Slack Sent'])

        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}
        config = testconfig
        config.MONITOR_CONFIG["environment"] = 'production'

        client_id = 85940
        trouble = 'LATENCY'

        err_msg = ("Outage ticket creation failed for edge host = mettel.velocloud.net, enterprise_id = 137, "
                   "edge_id = 1651. Reason: "
                   "Error 400 - Failed")
        uuid_ = uuid()

        slack_message = {
            'request_id': uuid_,
            'message': err_msg
        }
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_mock = None
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._ticket_object_to_string = Mock(return_value='Some string object')

        with patch.object(service_affecting_monitor_module, 'uuid', return_value=uuid_):
            await service_affecting_monitor._notify_trouble(link_info, trouble, ticket_dict)

        bruin_repository.get_affecting_ticket.assert_awaited_once_with(
            client_id, "VC05200028729")

        service_affecting_monitor._ticket_object_to_string.assert_called_once()
        event_bus.rpc_request.assert_awaited_with(
                                                   "notification.slack.request",
                                                   slack_message,
                                                   timeout=10
                                                 )
        metrics_repository.increment_tickets_created.assert_not_called()

    @pytest.mark.asyncio
    async def notify_trouble_pro_ticket_not_exists_success_rpc_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[{'body': {'ticketIds': [123]}, 'status': 200},
                                                           'Note Posted',
                                                           'Slack Sent'])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        metrics_repository.increment_tickets_created = Mock()

        config.MONITOR_CONFIG['environment'] = 'production'
        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        client_id = 85940
        trouble = 'LATENCY'

        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_mock = None
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._ticket_object_to_string = Mock(return_value='Some string object')

        await service_affecting_monitor._notify_trouble(link_info, trouble, ticket_dict)

        bruin_repository.get_affecting_ticket.assert_awaited_once_with(
            client_id, 'VC05200028729')

        service_affecting_monitor._ticket_object_to_string.assert_called_with(ticket_dict)

        metrics_repository.increment_tickets_created.assert_called_once()
        assert event_bus.rpc_request.called
        assert 'Some string object' == event_bus.rpc_request.mock_calls[1][1][1]['body']['note']

    @pytest.mark.asyncio
    async def notify_trouble_with_unknown_config_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value="Email Sent")
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()

        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602,
                "name": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        config = testconfig
        config.MONITOR_CONFIG['environment'] = None
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._template_renderer.compose_email_object = Mock(return_value='Some email object')

        await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._template_renderer.compose_email_object.assert_not_called()
        event_bus.rpc_request.assert_not_awaited()

    def compose_ticket_dict_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        link_1_best_latency_ms_rx = 14
        link_1_best_latency_ms_tx = 121

        link_info = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterpriseId": 137,
                "edgeId": 1602,
                "edgeName": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1',
                'displayName': 'Test'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_1_best_latency_ms_rx,
                'bestLatencyMsTx': link_1_best_latency_ms_tx,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict_1 = service_affecting_monitor._compose_ticket_dict(link_info,
                                                                       link_1_best_latency_ms_rx,
                                                                       link_1_best_latency_ms_tx,
                                                                       'LATENCY', 120)

        assert 'Receive' not in ticket_dict_1.keys()
        assert 'Transfer' in ticket_dict_1.keys()
        assert isinstance(ticket_dict_1, OrderedDict)

        link_2_best_latency_ms_rx = 141
        link_2_best_latency_ms_tx = 11

        link_info_2 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterpriseId": 137,
                "edgeId": 1602,
                "edgeName": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1',
                'displayName': 'Test'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_2_best_latency_ms_rx,
                'bestLatencyMsTx': link_2_best_latency_ms_tx,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict_2 = service_affecting_monitor._compose_ticket_dict(link_info_2,
                                                                       link_2_best_latency_ms_rx,
                                                                       link_2_best_latency_ms_tx,
                                                                       'LATENCY', 120)

        assert 'Receive' in ticket_dict_2.keys()
        assert 'Transfer' not in ticket_dict_2.keys()
        assert isinstance(ticket_dict_1, OrderedDict)

        link_3_best_latency_ms_rx = 141
        link_3_best_latency_ms_tx = 121

        link_info_3 = {
            'edge_status': {
                "host": "mettel.velocloud.net",
                "enterpriseId": 137,
                "edgeId": 1602,
                "edgeName": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"},
            'link_status': {
                'interface': 'GE1',
                'displayName': 'Test'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_3_best_latency_ms_rx,
                'bestLatencyMsTx': link_3_best_latency_ms_tx,
            },
            'cached_info': {'edge': {"host": "mettel.velocloud.net",
                                     "enterprise_id": 137,
                                     "edge_id": 1651},
                            'bruin_client_info': {'client_id': 85940},
                            'serial_number': 'VC05200028729'
                            },
            'contact_info': {
                "ticket": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                },
                "site": {
                    "email": "fake@gmail.com",
                    "phone": "111-111-1111",
                    "name": "Fake Guy",
                }
            }
        }

        ticket_dict_3 = service_affecting_monitor._compose_ticket_dict(link_info_3,
                                                                       link_3_best_latency_ms_rx,
                                                                       link_3_best_latency_ms_tx,
                                                                       'LATENCY', 120)

        assert 'Receive' in ticket_dict_3.keys()
        assert 'Transfer' in ticket_dict_3.keys()
        assert isinstance(ticket_dict_1, OrderedDict)

    def ticket_object_to_string_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_note = service_affecting_monitor._ticket_object_to_string(test_dict)
        assert ticket_note == '#*Automation Engine*# \nEdgeName: Test \nEdge Status: ok \n'

    def ticket_object_to_string_watermark_given_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        watermark = "Test "
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        ticket_note = service_affecting_monitor._ticket_object_to_string(test_dict, watermark)
        assert ticket_note == f'{watermark} \nEdgeName: Test \nEdge Status: ok \n'

    def structure_links_metrics_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        link_metrics = {
                            'linkId': 12,
                            'bytesTx': 289334426,
                            'bytesRx': 164603350,
                            'packetsTx': 1682073,
                            'packetsRx': 1610536,
                            'totalBytes': 453937776,
                            'totalPackets': 3292609,
                            'p1BytesRx': 20936271,
                            'p1BytesTx': 62441238,
                            'p1PacketsRx': 54742,
                            'p1PacketsTx': 92015,
                            'p2BytesRx': 46571112,
                            'p2BytesTx': 119887124,
                            'p2PacketsRx': 195272,
                            'p2PacketsTx': 246338,
                            'p3BytesRx': 2990392,
                            'p3BytesTx': 2273566,
                            'p3PacketsRx': 3054,
                            'p3PacketsTx': 5523,
                            'controlBytesRx': 94105575,
                            'controlBytesTx': 104732498,
                            'controlPacketsRx': 1357468,
                            'controlPacketsTx': 1338197,
                            'bpsOfBestPathRx': 682655000,
                            'bpsOfBestPathTx': 750187000,
                            'bestJitterMsRx': 0,
                            'bestJitterMsTx': 0,
                            'bestLatencyMsRx': 0,
                            'bestLatencyMsTx': 0,
                            'bestLossPctRx': 0,
                            'bestLossPctTx': 0,
                            'scoreTx': 4.400000095367432,
                            'scoreRx': 4.400000095367432,
                            'signalStrength': 0,
                            'state': 0,
                            'name': 'GE1',
                            'link': {
                                        'enterpriseName': 'Signet Group Services Inc|86937|',
                                        'enterpriseId': 2,
                                        'enterpriseProxyId': None,
                                        'enterpriseProxyName': None,
                                        'edgeName': 'LAB09910VC',
                                        'edgeState': 'CONNECTED',
                                        'edgeSystemUpSince': '2020-09-23T04:59:12.000Z',
                                        'edgeServiceUpSince': '2020-09-23T05:00:03.000Z',
                                        'edgeLastContact': '2020-09-29T05:09:24.000Z',
                                        'edgeId': 4,
                                        'edgeSerialNumber': 'VC05200005831',
                                        'edgeHASerialNumber': None,
                                        'edgeModelNumber': 'edge520',
                                        'edgeLatitude': 41.139999,
                                        'edgeLongitude': -81.612999,
                                        'displayName': '198.70.201.220',
                                        'isp': 'Frontier Communications',
                                        'interface': 'GE1',
                                        'internalId': '00000001-a028-4037-a4bc-4d0488f4c9f9',
                                        'linkState': 'STABLE',
                                        'linkLastActive': '2020-09-29T05:05:23.000Z',
                                        'linkVpnState': 'STABLE',
                                        'linkId': 12,
                                        'linkIpAddress': '198.70.201.220',
                                        'host': 'some host'
                            },
                        }
        expected_link_structure = {
                'edge_status': {
                    'enterpriseName': link_metrics['link']['enterpriseName'],
                    'enterpriseId': link_metrics['link']['enterpriseId'],
                    'enterpriseProxyId': link_metrics['link']['enterpriseProxyId'],
                    'enterpriseProxyName': link_metrics['link']['enterpriseProxyName'],
                    'edgeName': link_metrics['link']['edgeName'],
                    'edgeState': link_metrics['link']['edgeState'],
                    'edgeSystemUpSince': link_metrics['link']['edgeSystemUpSince'],
                    'edgeServiceUpSince': link_metrics['link']['edgeServiceUpSince'],
                    'edgeLastContact': link_metrics['link']['edgeLastContact'],
                    'edgeId': link_metrics['link']['edgeId'],
                    'edgeSerialNumber': link_metrics['link']['edgeSerialNumber'],
                    'edgeHASerialNumber': link_metrics['link']['edgeHASerialNumber'],
                    'edgeModelNumber': link_metrics['link']['edgeModelNumber'],
                    'edgeLatitude': link_metrics['link']['edgeLatitude'],
                    'edgeLongitude': link_metrics['link']['edgeLongitude'],
                    'host': link_metrics['link']['host'],
                },
                'link_status': {
                    'interface': link_metrics['link']['interface'],
                    'internalId': link_metrics['link']['internalId'],
                    'linkState': link_metrics['link']['linkState'],
                    'linkLastActive': link_metrics['link']['linkLastActive'],
                    'linkVpnState': link_metrics['link']['linkVpnState'],
                    'linkId': link_metrics['link']['linkId'],
                    'linkIpAddress': link_metrics['link']['linkIpAddress'],
                    'displayName': link_metrics['link']['displayName'],
                    'isp': link_metrics['link']['isp'],
                },
                'link_metrics': {
                    'bytesTx': link_metrics['bytesTx'],
                    'bytesRx': link_metrics['bytesRx'],
                    'packetsTx': link_metrics['packetsTx'],
                    'packetsRx': link_metrics['packetsRx'],
                    'totalBytes': link_metrics['totalBytes'],
                    'totalPackets': link_metrics['totalPackets'],
                    'p1BytesRx': link_metrics['p1BytesRx'],
                    'p1BytesTx': link_metrics['p1BytesTx'],
                    'p1PacketsRx': link_metrics['p1PacketsRx'],
                    'p1PacketsTx': link_metrics['p1PacketsTx'],
                    'p2BytesRx': link_metrics['p2BytesRx'],
                    'p2BytesTx': link_metrics['p2BytesTx'],
                    'p2PacketsRx': link_metrics['p2PacketsRx'],
                    'p2PacketsTx': link_metrics['p2PacketsTx'],
                    'p3BytesRx': link_metrics['p3BytesRx'],
                    'p3BytesTx': link_metrics['p3BytesTx'],
                    'p3PacketsRx': link_metrics['p3PacketsRx'],
                    'p3PacketsTx': link_metrics['p3PacketsTx'],
                    'controlBytesRx': link_metrics['controlBytesRx'],
                    'controlBytesTx': link_metrics['controlBytesTx'],
                    'controlPacketsRx': link_metrics['controlPacketsRx'],
                    'controlPacketsTx': link_metrics['controlPacketsTx'],
                    'bpsOfBestPathRx': link_metrics['bpsOfBestPathRx'],
                    'bpsOfBestPathTx': link_metrics['bpsOfBestPathTx'],
                    'bestJitterMsRx': link_metrics['bestJitterMsRx'],
                    'bestJitterMsTx': link_metrics['bestJitterMsTx'],
                    'bestLatencyMsRx': link_metrics['bestLatencyMsRx'],
                    'bestLatencyMsTx': link_metrics['bestLatencyMsTx'],
                    'bestLossPctRx': link_metrics['bestLossPctRx'],
                    'bestLossPctTx': link_metrics['bestLossPctTx'],
                    'scoreTx': link_metrics['scoreTx'],
                    'scoreRx': link_metrics['scoreRx'],
                    'signalStrength': link_metrics['signalStrength'],
                    'state': link_metrics['state'],
                }
            }
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        structure_links = service_affecting_monitor._structure_links_metrics([link_metrics])
        assert structure_links == [expected_link_structure]

    def structure_links_metrics_no_edge_id_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        link_metrics = {
                            'linkId': 12,
                            'bytesTx': 289334426,
                            'bytesRx': 164603350,
                            'packetsTx': 1682073,
                            'packetsRx': 1610536,
                            'totalBytes': 453937776,
                            'totalPackets': 3292609,
                            'p1BytesRx': 20936271,
                            'p1BytesTx': 62441238,
                            'p1PacketsRx': 54742,
                            'p1PacketsTx': 92015,
                            'p2BytesRx': 46571112,
                            'p2BytesTx': 119887124,
                            'p2PacketsRx': 195272,
                            'p2PacketsTx': 246338,
                            'p3BytesRx': 2990392,
                            'p3BytesTx': 2273566,
                            'p3PacketsRx': 3054,
                            'p3PacketsTx': 5523,
                            'controlBytesRx': 94105575,
                            'controlBytesTx': 104732498,
                            'controlPacketsRx': 1357468,
                            'controlPacketsTx': 1338197,
                            'bpsOfBestPathRx': 682655000,
                            'bpsOfBestPathTx': 750187000,
                            'bestJitterMsRx': 0,
                            'bestJitterMsTx': 0,
                            'bestLatencyMsRx': 0,
                            'bestLatencyMsTx': 0,
                            'bestLossPctRx': 0,
                            'bestLossPctTx': 0,
                            'scoreTx': 4.400000095367432,
                            'scoreRx': 4.400000095367432,
                            'signalStrength': 0,
                            'state': 0,
                            'name': 'GE1',
                            'link': {
                                        'enterpriseName': 'Signet Group Services Inc|86937|',
                                        'enterpriseId': 2,
                                        'enterpriseProxyId': None,
                                        'enterpriseProxyName': None,
                                        'edgeName': 'LAB09910VC',
                                        'edgeState': 'CONNECTED',
                                        'edgeSystemUpSince': '2020-09-23T04:59:12.000Z',
                                        'edgeServiceUpSince': '2020-09-23T05:00:03.000Z',
                                        'edgeLastContact': '2020-09-29T05:09:24.000Z',
                                        'edgeSerialNumber': 'VC05200005831',
                                        'edgeHASerialNumber': None,
                                        'edgeModelNumber': 'edge520',
                                        'edgeLatitude': 41.139999,
                                        'edgeLongitude': -81.612999,
                                        'displayName': '198.70.201.220',
                                        'isp': 'Frontier Communications',
                                        'interface': 'GE1',
                                        'internalId': '00000001-a028-4037-a4bc-4d0488f4c9f9',
                                        'linkState': 'STABLE',
                                        'linkLastActive': '2020-09-29T05:05:23.000Z',
                                        'linkVpnState': 'STABLE',
                                        'linkId': 12,
                                        'linkIpAddress': '198.70.201.220',
                                        'host': 'some host'
                            },
                        }

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        structure_links = service_affecting_monitor._structure_links_metrics([link_metrics])
        assert structure_links == []

    def map_cached_edges_with_links_metrics_and_contact_info_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        link_metrics = {
                            'linkId': 12,
                            'bytesTx': 289334426,
                            'bytesRx': 164603350,
                            'packetsTx': 1682073,
                            'packetsRx': 1610536,
                            'totalBytes': 453937776,
                            'totalPackets': 3292609,
                            'p1BytesRx': 20936271,
                            'p1BytesTx': 62441238,
                            'p1PacketsRx': 54742,
                            'p1PacketsTx': 92015,
                            'p2BytesRx': 46571112,
                            'p2BytesTx': 119887124,
                            'p2PacketsRx': 195272,
                            'p2PacketsTx': 246338,
                            'p3BytesRx': 2990392,
                            'p3BytesTx': 2273566,
                            'p3PacketsRx': 3054,
                            'p3PacketsTx': 5523,
                            'controlBytesRx': 94105575,
                            'controlBytesTx': 104732498,
                            'controlPacketsRx': 1357468,
                            'controlPacketsTx': 1338197,
                            'bpsOfBestPathRx': 682655000,
                            'bpsOfBestPathTx': 750187000,
                            'bestJitterMsRx': 0,
                            'bestJitterMsTx': 0,
                            'bestLatencyMsRx': 0,
                            'bestLatencyMsTx': 0,
                            'bestLossPctRx': 0,
                            'bestLossPctTx': 0,
                            'scoreTx': 4.400000095367432,
                            'scoreRx': 4.400000095367432,
                            'signalStrength': 0,
                            'state': 0,
                            'name': 'GE1',
                            'link': {
                                        'enterpriseName': 'Signet Group Services Inc|86937|',
                                        'enterpriseId': 137,
                                        'enterpriseProxyId': None,
                                        'enterpriseProxyName': None,
                                        'edgeName': 'LAB09910VC',
                                        'edgeState': 'CONNECTED',
                                        'edgeSystemUpSince': '2020-09-23T04:59:12.000Z',
                                        'edgeServiceUpSince': '2020-09-23T05:00:03.000Z',
                                        'edgeLastContact': '2020-09-29T05:09:24.000Z',
                                        'edgeId': 1651,
                                        'edgeSerialNumber': 'VC05200005831',
                                        'edgeHASerialNumber': None,
                                        'edgeModelNumber': 'edge520',
                                        'edgeLatitude': 41.139999,
                                        'edgeLongitude': -81.612999,
                                        'displayName': '198.70.201.220',
                                        'isp': 'Frontier Communications',
                                        'interface': 'GE1',
                                        'internalId': '00000001-a028-4037-a4bc-4d0488f4c9f9',
                                        'linkState': 'STABLE',
                                        'linkLastActive': '2020-09-29T05:05:23.000Z',
                                        'linkVpnState': 'STABLE',
                                        'linkId': 12,
                                        'linkIpAddress': '198.70.201.220',
                                        'host': 'mettel.velocloud.net'
                            },
                        }
        link_structure = {
                'edge_status': {
                    'enterpriseName': link_metrics['link']['enterpriseName'],
                    'enterpriseId': link_metrics['link']['enterpriseId'],
                    'enterpriseProxyId': link_metrics['link']['enterpriseProxyId'],
                    'enterpriseProxyName': link_metrics['link']['enterpriseProxyName'],
                    'edgeName': link_metrics['link']['edgeName'],
                    'edgeState': link_metrics['link']['edgeState'],
                    'edgeSystemUpSince': link_metrics['link']['edgeSystemUpSince'],
                    'edgeServiceUpSince': link_metrics['link']['edgeServiceUpSince'],
                    'edgeLastContact': link_metrics['link']['edgeLastContact'],
                    'edgeId': link_metrics['link']['edgeId'],
                    'edgeSerialNumber': link_metrics['link']['edgeSerialNumber'],
                    'edgeHASerialNumber': link_metrics['link']['edgeHASerialNumber'],
                    'edgeModelNumber': link_metrics['link']['edgeModelNumber'],
                    'edgeLatitude': link_metrics['link']['edgeLatitude'],
                    'edgeLongitude': link_metrics['link']['edgeLongitude'],
                    'host': link_metrics['link']['host'],
                },
                'link_status': {
                    'interface': link_metrics['link']['interface'],
                    'internalId': link_metrics['link']['internalId'],
                    'linkState': link_metrics['link']['linkState'],
                    'linkLastActive': link_metrics['link']['linkLastActive'],
                    'linkVpnState': link_metrics['link']['linkVpnState'],
                    'linkId': link_metrics['link']['linkId'],
                    'linkIpAddress': link_metrics['link']['linkIpAddress'],
                    'displayName': link_metrics['link']['displayName'],
                    'isp': link_metrics['link']['isp'],
                },
                'link_metrics': {
                    'bytesTx': link_metrics['bytesTx'],
                    'bytesRx': link_metrics['bytesRx'],
                    'packetsTx': link_metrics['packetsTx'],
                    'packetsRx': link_metrics['packetsRx'],
                    'totalBytes': link_metrics['totalBytes'],
                    'totalPackets': link_metrics['totalPackets'],
                    'p1BytesRx': link_metrics['p1BytesRx'],
                    'p1BytesTx': link_metrics['p1BytesTx'],
                    'p1PacketsRx': link_metrics['p1PacketsRx'],
                    'p1PacketsTx': link_metrics['p1PacketsTx'],
                    'p2BytesRx': link_metrics['p2BytesRx'],
                    'p2BytesTx': link_metrics['p2BytesTx'],
                    'p2PacketsRx': link_metrics['p2PacketsRx'],
                    'p2PacketsTx': link_metrics['p2PacketsTx'],
                    'p3BytesRx': link_metrics['p3BytesRx'],
                    'p3BytesTx': link_metrics['p3BytesTx'],
                    'p3PacketsRx': link_metrics['p3PacketsRx'],
                    'p3PacketsTx': link_metrics['p3PacketsTx'],
                    'controlBytesRx': link_metrics['controlBytesRx'],
                    'controlBytesTx': link_metrics['controlBytesTx'],
                    'controlPacketsRx': link_metrics['controlPacketsRx'],
                    'controlPacketsTx': link_metrics['controlPacketsTx'],
                    'bpsOfBestPathRx': link_metrics['bpsOfBestPathRx'],
                    'bpsOfBestPathTx': link_metrics['bpsOfBestPathTx'],
                    'bestJitterMsRx': link_metrics['bestJitterMsRx'],
                    'bestJitterMsTx': link_metrics['bestJitterMsTx'],
                    'bestLatencyMsRx': link_metrics['bestLatencyMsRx'],
                    'bestLatencyMsTx': link_metrics['bestLatencyMsTx'],
                    'bestLossPctRx': link_metrics['bestLossPctRx'],
                    'bestLossPctTx': link_metrics['bestLossPctTx'],
                    'scoreTx': link_metrics['scoreTx'],
                    'scoreRx': link_metrics['scoreRx'],
                    'signalStrength': link_metrics['signalStrength'],
                    'state': link_metrics['state'],
                }
            }
        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651
        }
        device_2 = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }
        contact_info = {
            "ticket": {
                "email": "mettel_alerts@titanamerica.com",
                "phone": "757-533-7151",
                "name": "Gary Clark"
            },
            "site": {
                "email": "mettel_alerts@titanamerica.com",
                "phone": "757-533-7151",
                "name": "Gary Clark"
            }
        }
        customer_cache_repository = [{'edge': device}, {'edge': device_2}]
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._customer_cache = customer_cache_repository
        map_cached_edges_with_links_metrics = service_affecting_monitor.\
            _map_cached_edges_with_links_metrics_and_contact_info([link_structure])
        assert map_cached_edges_with_links_metrics == [{
                                                        'cached_info': customer_cache_repository[0],
                                                        'contact_info': contact_info,
                                                        **link_structure,
                                                     }]

    def ticket_object_to_string_without_watermark_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        ticket_dict = {'ticket': 'some ticket details'}

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository)
        service_affecting_monitor._ticket_object_to_string = Mock()

        service_affecting_monitor._ticket_object_to_string_without_watermark(ticket_dict)

        service_affecting_monitor._ticket_object_to_string.assert_called_once_with(ticket_dict, "")
