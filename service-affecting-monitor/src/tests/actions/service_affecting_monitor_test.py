from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from apscheduler.util import undefined
from asynctest import CoroutineMock
from dateutil.parser import parse
from pytz import utc
from shortuuid import uuid

from application.actions import service_affecting_monitor as service_affecting_monitor_module
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        assert service_affecting_monitor._event_bus is event_bus
        assert service_affecting_monitor._logger is logger
        assert service_affecting_monitor._scheduler is scheduler
        assert service_affecting_monitor._config is config
        assert service_affecting_monitor._metrics_repository is metrics_repository
        assert service_affecting_monitor._bruin_repository is bruin_repository
        assert service_affecting_monitor._velocloud_repository is velocloud_repository
        assert service_affecting_monitor._customer_cache_repository is customer_cache_repository
        assert service_affecting_monitor._notifications_repository is notifications_repository

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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        notifications_repository = Mock()

        customer_cache_list = ['edges']
        customer_cache_return = {
            "body": customer_cache_list,
            "status": 200
        }
        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=customer_cache_return)

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._latency_check = CoroutineMock()
        service_affecting_monitor._packet_loss_check = CoroutineMock()
        service_affecting_monitor._jitter_check = CoroutineMock()
        service_affecting_monitor._bandwidth_check = CoroutineMock()
        service_affecting_monitor._run_autoresolve_process = CoroutineMock()

        await service_affecting_monitor._service_affecting_monitor_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_awaited_once()
        service_affecting_monitor._packet_loss_check.assert_awaited_once()
        service_affecting_monitor._jitter_check.assert_awaited_once()
        service_affecting_monitor._bandwidth_check.assert_awaited_once()
        service_affecting_monitor._run_autoresolve_process.assert_awaited_once()

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
        notifications_repository = Mock()

        customer_cache_list = ['edges']
        customer_cache_return = {
            "body": customer_cache_list,
            "status": 500
        }
        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=customer_cache_return)

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._latency_check = CoroutineMock()
        service_affecting_monitor._packet_loss_check = CoroutineMock()
        service_affecting_monitor._jitter_check = CoroutineMock()
        service_affecting_monitor._bandwidth_check = CoroutineMock()
        service_affecting_monitor._run_autoresolve_process = CoroutineMock()

        await service_affecting_monitor._service_affecting_monitor_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_not_awaited()
        service_affecting_monitor._packet_loss_check.assert_not_awaited()
        service_affecting_monitor._jitter_check.assert_not_awaited()
        service_affecting_monitor._bandwidth_check.assert_not_awaited()
        service_affecting_monitor._run_autoresolve_process.assert_not_awaited()

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
        notifications_repository = Mock()

        customer_cache_list = []
        customer_cache_return = {
            "body": customer_cache_list,
            "status": 200
        }
        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=customer_cache_return)

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._latency_check = CoroutineMock()
        service_affecting_monitor._packet_loss_check = CoroutineMock()
        service_affecting_monitor._jitter_check = CoroutineMock()
        service_affecting_monitor._bandwidth_check = CoroutineMock()
        service_affecting_monitor._run_autoresolve_process = CoroutineMock()

        await service_affecting_monitor._service_affecting_monitor_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_not_awaited()
        service_affecting_monitor._packet_loss_check.assert_not_awaited()
        service_affecting_monitor._jitter_check.assert_not_awaited()
        service_affecting_monitor._bandwidth_check.assert_not_awaited()
        service_affecting_monitor._run_autoresolve_process.assert_not_awaited()

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
                "enterprise_name": "Titan America|85940|"
            },
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
                "enterprise_name": "Titan America|85940|"
            },
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
                "enterprise_name": "Titan America|85940|"
            },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        link_best_latency_ms_tx = 141

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
                "enterprise_name": "Titan America|85940|"
            },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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

        link_best_latency_ms_rx = 141
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
                "enterprise_name": "Titan America|85940|"
            },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
                "enterprise_name": "Titan America|85940|"
            },
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
                "enterprise_name": "Titan America|85940|"
            },
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
                "enterprise_name": "Titan America|85940|"
            },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
                "enterprise_name": "Titan America|85940|"
            },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
                "enterprise_name": "Titan America|85940|"
            },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
                "enterprise_name": "Titan America|85940|"
            },
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
                "enterprise_name": "Titan America|85940|"
            },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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

        link_1_best_jitter_ms_rx = 52
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
                "enterprise_name": "Titan America|85940|"
            },
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
                "enterprise_name": "Titan America|85940|"
            },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
    async def bandwidth_check_with_no_troubles_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_bandwidth_bps_rx = 100
        link_1_bandwidth_bps_tx = 100
        link_1_bytes_rx = 1200
        link_1_bytes_tx = 1300

        link_2_bandwidth_bps_rx = 100
        link_2_bandwidth_bps_tx = 100
        link_2_bytes_rx = 1500
        link_2_bytes_tx = 1700

        link_3_bandwidth_bps_rx = 100
        link_3_bandwidth_bps_tx = 100
        link_3_bytes_rx = 2000
        link_3_bytes_tx = 2200

        link_1 = {
            'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
            'bytesTx': link_1_bytes_tx,
            'bytesRx': link_1_bytes_rx,
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
            'bpsOfBestPathTx': link_2_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_2_bandwidth_bps_rx,
            'bytesTx': link_2_bytes_tx,
            'bytesRx': link_2_bytes_rx,
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
            'bpsOfBestPathTx': link_3_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_3_bandwidth_bps_rx,
            'bytesTx': link_3_bytes_tx,
            'bytesRx': link_3_bytes_rx,
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE2'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE3'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
            }
        }
        structure_link_return = [structure_link_1,
                                 structure_link_2,
                                 structure_link_3]
        metrics_with_cache_and_contact_info_return = [
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_1
            },
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_2
            },
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_3
            }]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_bandwidth_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)
        service_affecting_monitor._is_rep_services_client_id = Mock(return_value=True)
        service_affecting_monitor._compose_bandwidth_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._bandwidth_check()

        velocloud_repository.get_links_metrics_for_bandwidth_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_bandwidth_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check_empty_link_metrics_test(self):
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
        velocloud_repository.get_links_metrics_for_bandwidth_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._structure_links_metrics = Mock()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock()
        service_affecting_monitor._compose_bandwidth_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._bandwidth_check()

        velocloud_repository.get_links_metrics_for_bandwidth_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._compose_bandwidth_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check_with_invalid_rx_and_tx_bandwidth_metrics_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_bandwidth_bps_rx = 0
        link_1_bandwidth_bps_tx = 0
        link_1_bytes_rx = 1200
        link_1_bytes_tx = 1300

        link_2_bandwidth_bps_rx = 0
        link_2_bandwidth_bps_tx = 0
        link_2_bytes_rx = 1500
        link_2_bytes_tx = 1700

        link_3_bandwidth_bps_rx = 0
        link_3_bandwidth_bps_tx = 0
        link_3_bytes_rx = 2000
        link_3_bytes_tx = 2200

        link_1 = {
            'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
            'bytesTx': link_1_bytes_tx,
            'bytesRx': link_1_bytes_rx,
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
            'bpsOfBestPathTx': link_2_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_2_bandwidth_bps_rx,
            'bytesTx': link_2_bytes_tx,
            'bytesRx': link_2_bytes_rx,
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
            'bpsOfBestPathTx': link_3_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_3_bandwidth_bps_rx,
            'bytesTx': link_3_bytes_tx,
            'bytesRx': link_3_bytes_rx,
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE2'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE3'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
            }
        }
        structure_link_return = [structure_link_1,
                                 structure_link_2,
                                 structure_link_3]
        metrics_with_cache_and_contact_info_return = [
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_1
            },
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_2
            },
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_3
            }]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_bandwidth_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)
        service_affecting_monitor._is_rep_services_client_id = Mock(return_value=True)
        service_affecting_monitor._compose_bandwidth_ticket_dict = Mock()
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._bandwidth_check()

        velocloud_repository.get_links_metrics_for_bandwidth_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_bandwidth_ticket_dict.assert_not_called()
        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check_with_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_bandwidth_bps_rx = 100
        link_1_bandwidth_bps_tx = 100
        link_1_bytes_rx = 1500
        link_1_bytes_tx = 21000

        link_1 = {
            'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
            'bytesTx': link_1_bytes_tx,
            'bytesRx': link_1_bytes_rx,
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
                "enterpriseId": 137,
                "edgeId": 1602,
                "edgeName": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1',
                'displayName': 'GE1'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
            }
        }

        structure_link_return = [structure_link_1]
        metrics_with_cache_and_contact_info_return = [
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_1
            }]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_bandwidth_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)
        service_affecting_monitor._is_rep_services_client_id = Mock(return_value=True)

        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._bandwidth_check()

        velocloud_repository.get_links_metrics_for_bandwidth_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._notify_trouble.assert_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check_with_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_bandwidth_bps_rx = 100
        link_1_bandwidth_bps_tx = 100
        link_1_bytes_rx = 21000
        link_1_bytes_tx = 1200

        link_1 = {
            'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
            'bytesTx': link_1_bytes_tx,
            'bytesRx': link_1_bytes_rx,
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
                "enterpriseId": 137,
                "edgeId": 1602,
                "edgeName": "TEST",
                "edgeState": "OFFLINE",
                "serialNumber": "VC05200028729",
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1',
                'displayName': 'GE1'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
            }
        }

        structure_link_return = [structure_link_1]
        metrics_with_cache_and_contact_info_return = [
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_1
            }]

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_bandwidth_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)
        service_affecting_monitor._is_rep_services_client_id = Mock(return_value=True)

        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._bandwidth_check()

        velocloud_repository.get_links_metrics_for_bandwidth_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._notify_trouble.assert_awaited()

    @pytest.mark.asyncio
    async def bandwidth_check_with_link_and_rx_plus_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_1_bandwidth_bps_rx = 100
        link_1_bandwidth_bps_tx = 100
        link_1_bytes_rx = 21000
        link_1_bytes_tx = 21000

        link_1 = {
            'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
            'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
            'bytesTx': link_1_bytes_tx,
            'bytesRx': link_1_bytes_rx,
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bpsOfBestPathTx': link_1_bandwidth_bps_tx,
                'bpsOfBestPathRx': link_1_bandwidth_bps_rx,
                'bytesTx': link_1_bytes_tx,
                'bytesRx': link_1_bytes_rx,
            }
        }

        structure_link_return = [structure_link_1]
        metrics_with_cache_and_contact_info_return = [
            {
                'cached_info': {'edge': device, 'bruin_client_info': {'client_id': 83109}},
                'contact_info': "some_contact_info", **structure_link_1
            }]

        bandwidth_metrics = {
            'rx_throughput': 93.33333333333333,
            'rx_bandwidth': link_1_bandwidth_bps_rx,
            'rx_threshold': 90,
            'tx_throughput': 93.33333333333333,
            'tx_bandwidth': link_1_bandwidth_bps_tx,
            'tx_threshold': 90,
        }

        logger = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_bandwidth_checks = CoroutineMock(return_value=link_metrics_return)

        customer_cache_repository = Mock()
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structure_link_return)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=metrics_with_cache_and_contact_info_return)

        ticket_dict = {'ticket': 'some ticket details'}
        service_affecting_monitor._compose_bandwidth_ticket_dict = Mock(return_value=ticket_dict)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._bandwidth_check()

        velocloud_repository.get_links_metrics_for_bandwidth_checks.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_with(links_metric_body)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_with(
            structure_link_return)
        service_affecting_monitor._compose_bandwidth_ticket_dict.assert_called_once_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            bandwidth_metrics=bandwidth_metrics,
        )
        service_affecting_monitor._notify_trouble.assert_awaited_with(
            link_info=metrics_with_cache_and_contact_info_return[0],
            trouble='Bandwidth Over Utilization',
            ticket_dict=ticket_dict,
        )

    @pytest.mark.asyncio
    async def run_autoresolve_process_ok_test(self):
        host = 'mettel.velocloud.net'
        enterprise_id = 2
        edge_id = 4206
        serial_number = 'VC05200048223'

        contact_info = {
            'ticket': {
                'email': 'fake@mail.com',
                'phone': '6666666666',
                'name': 'Fake'
            },
            'site': {
                'email': 'fake@mail.com',
                'phone': '6666666666',
                'name': 'Fake'
            },
        }

        edge_status = {
            'host': host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_id,
            'edgeSerialNumber': serial_number,
            # Some fields omitted for simplicity
        }
        edge_cached_info = {
            'edge': {
                'host': host,
                'enterprise_id': enterprise_id,
                'edge_id': edge_id
            },
            'serial_number': serial_number,
            'bruin_client_info': {
                'client_id': 30000,
                'client_name': 'MetTel',
            },
            # Some fields omitted for simplicity
        }

        link_1_status = {
            'displayName': '70.59.5.185',
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
            # Some fields omitted for simplicity
        }
        link_1_metrics = {
            'bytesTx': 5694196,
            'bytesRx': 9607567,
            'bpsOfBestPathRx': 182296000,
            'bpsOfBestPathTx': 43243000,
            'bestJitterMsRx': 0,
            'bestJitterMsTx': 0,
            'bestLatencyMsRx': 3,
            'bestLatencyMsTx': 6.4167,
            'bestLossPctRx': 0,
            'bestLossPctTx': 0,
            # Some fields omitted for simplicity
        }
        link_1_metrics_object = {
            **link_1_metrics,
            'link': {
                **edge_status,
                **link_1_status,
            },
        }

        link_2_status = {
            'displayName': '70.59.5.186',
            'interface': 'RAY',
            'linkState': 'STABLE',
            'linkId': 5294,
            # Some fields omitted for simplicity
        }
        link_2_metrics = {
            'bytesTx': 5694197,
            'bytesRx': 9607568,
            'bpsOfBestPathRx': 182296001,
            'bpsOfBestPathTx': 43243001,
            'bestJitterMsRx': 1,
            'bestJitterMsTx': 1,
            'bestLatencyMsRx': 4,
            'bestLatencyMsTx': 6.4168,
            'bestLossPctRx': 1,
            'bestLossPctTx': 1,
            # Some fields omitted for simplicity
        }
        link_2_metrics_object = {
            **link_2_metrics,
            'link': {
                **edge_status,
                **link_2_status,
            },
        }

        links_metrics_objects = [
            link_1_metrics_object,
            link_2_metrics_object,
        ]
        links_metrics_response = {
            'request_id': uuid_,
            'body': links_metrics_objects,
            'status': 200,
        }

        structured_link_1 = {
            'edge_status': edge_status,
            'link_status': link_1_status,
            'link_metrics': link_1_metrics,
        }
        structured_link_2 = {
            'edge_status': edge_status,
            'link_status': link_2_status,
            'link_metrics': link_2_metrics,
        }
        structured_links = [
            structured_link_1,
            structured_link_2,
        ]

        link_1_metrics_with_cache_and_contact_info = {
            'cached_info': edge_cached_info,
            'contact_info': contact_info,
            **structured_link_1,
        }
        link_2_metrics_with_cache_and_contact_info = {
            'cached_info': edge_cached_info,
            'contact_info': contact_info,
            **structured_link_2,
        }
        links_metrics_with_cache_and_contact_info = [
            link_1_metrics_with_cache_and_contact_info,
            link_2_metrics_with_cache_and_contact_info,
        ]

        edge_with_links_info = {
            'cached_info': edge_cached_info,
            'contact_info': contact_info,
            'edge_status': edge_status,
            'links': [
                {
                    'link_status': link_1_status,
                    'link_metrics': link_1_metrics,
                },
                {
                    'link_status': link_2_status,
                    'link_metrics': link_2_metrics,
                },
            ]
        }
        edges_with_links_info = [
            edge_with_links_info,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_autoresolve = CoroutineMock(return_value=links_metrics_response)

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._structure_links_metrics = Mock(return_value=structured_links)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock(
            return_value=links_metrics_with_cache_and_contact_info
        )
        service_affecting_monitor._group_links_by_edge = Mock(return_value=edges_with_links_info)
        service_affecting_monitor._run_autoresolve_for_edge = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_process()

        velocloud_repository.get_links_metrics_for_autoresolve.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_called_once_with(links_metrics_objects)
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_called_once_with(
            structured_links
        )
        service_affecting_monitor._group_links_by_edge.assert_called_once_with(
            links_metrics_with_cache_and_contact_info
        )
        service_affecting_monitor._run_autoresolve_for_edge.assert_has_awaits([
            call(edge_with_links_info),
        ])

    @pytest.mark.asyncio
    async def run_autoresolve_process_with_no_links_metrics_test(self):
        links_metrics_response = {
            'request_id': uuid_,
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_metrics_for_autoresolve = CoroutineMock(return_value=links_metrics_response)

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._structure_links_metrics = Mock()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info = Mock()
        service_affecting_monitor._group_links_by_edge = Mock()
        service_affecting_monitor._run_autoresolve_for_edge = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_process()

        velocloud_repository.get_links_metrics_for_autoresolve.assert_awaited_once()
        service_affecting_monitor._structure_links_metrics.assert_not_called()
        service_affecting_monitor._map_cached_edges_with_links_metrics_and_contact_info.assert_not_called()
        service_affecting_monitor._group_links_by_edge.assert_not_called()
        service_affecting_monitor._run_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_metrics_above_thresholds_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500000,
                        'bytesRx': 500000,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600000,
                        'bytesRx': 600000,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=False)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock()
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock()
        service_affecting_monitor._is_ticket_resolved = Mock()
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_not_awaited()
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_not_called()
        bruin_repository.get_ticket_details.assert_not_awaited()
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_not_called()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_not_called()
        service_affecting_monitor._is_ticket_resolved.assert_not_called()
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_get_affecting_tickets_rpc_having_non_2xx_status_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_tickets_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock()
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock()
        service_affecting_monitor._is_ticket_resolved = Mock()
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_not_called()
        bruin_repository.get_ticket_details.assert_not_awaited()
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_not_called()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_not_called()
        service_affecting_monitor._is_ticket_resolved.assert_not_called()
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_empty_list_of_affecting_tickets_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_tickets_response = {
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock()
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock()
        service_affecting_monitor._is_ticket_resolved = Mock()
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_not_called()
        bruin_repository.get_ticket_details.assert_not_awaited()
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_not_called()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_not_called()
        service_affecting_monitor._is_ticket_resolved.assert_not_called()
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_affecting_tickets_not_created_by_automation_engine_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_ticket_1 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": 12345,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "Gray Fox",
        }
        affecting_ticket_2 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": 67890,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 8:31:54 AM",
            "createdBy": "Raiden",
        }
        affecting_tickets_response = {
            'body': [
                affecting_ticket_1,
                affecting_ticket_2,
            ],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock(return_value=False)
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock()
        service_affecting_monitor._is_ticket_resolved = Mock()
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_has_calls([
            call(affecting_ticket_1),
            call(affecting_ticket_2),
        ])
        bruin_repository.get_ticket_details.assert_not_awaited()
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_not_called()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_not_called()
        service_affecting_monitor._is_ticket_resolved.assert_not_called()
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_get_ticket_details_rpc_having_non_2xx_status_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_ticket_1_id = 12345
        affecting_ticket_2_id = 67890

        affecting_ticket_1 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "Intelygenz Ai",
        }
        affecting_ticket_2 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_2_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 8:31:54 AM",
            "createdBy": "Intelygenz Ai",
        }
        affecting_tickets_response = {
            'body': [
                affecting_ticket_1,
                affecting_ticket_2,
            ],
            'status': 200,
        }

        ticket_details_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock()
        service_affecting_monitor._is_ticket_resolved = Mock()
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_has_calls([
            call(affecting_ticket_1),
            call(affecting_ticket_2),
        ])
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(affecting_ticket_1_id),
            call(affecting_ticket_2_id),
        ])
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_not_called()
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_not_called()
        service_affecting_monitor._is_ticket_resolved.assert_not_called()
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_last_affecting_trouble_detected_long_time_ago_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_ticket_1_id = 12345
        affecting_ticket_2_id = 67890

        affecting_ticket_1_creation_date = '9/25/2020 6:31:54 AM'
        affecting_ticket_2_creation_date = '9/25/2020 8:31:54 AM'

        affecting_ticket_1 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_ticket_2 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_2_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_2_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_tickets_response = {
            'body': [
                affecting_ticket_1,
                affecting_ticket_2,
            ],
            'status': 200,
        }

        affecting_ticket_1_detail = {
            "detailID": 5217537,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_1_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Latency\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_1_details_object = {
            'ticketDetails': [
                affecting_ticket_1_detail,
            ],
            'ticketNotes': affecting_ticket_1_notes,
        }

        affecting_ticket_2_detail = {
            "detailID": 5217666,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_2_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Packet Loss\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_2_details_object = {
            'ticketDetails': [
                affecting_ticket_2_detail,
            ],
            'ticketNotes': affecting_ticket_2_notes,
        }

        ticket_details_response_1 = {
            'body': affecting_ticket_1_details_object,
            'status': 200,
        }
        ticket_details_response_2 = {
            'body': affecting_ticket_2_details_object,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            ticket_details_response_1,
            ticket_details_response_2,
        ])
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock(return_value=False)
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock()
        service_affecting_monitor._is_ticket_resolved = Mock()
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_has_calls([
            call(affecting_ticket_1),
            call(affecting_ticket_2),
        ])
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(affecting_ticket_1_id),
            call(affecting_ticket_2_id),
        ])
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_has_calls([
            call(affecting_ticket_1_notes, affecting_ticket_1_creation_date),
            call(affecting_ticket_2_notes, affecting_ticket_2_creation_date),
        ])
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_not_called()
        service_affecting_monitor._is_ticket_resolved.assert_not_called()
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_affecting_ticket_not_being_autoresolvable_anymore_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_ticket_1_id = 12345
        affecting_ticket_2_id = 67890

        affecting_ticket_1_creation_date = '9/25/2020 6:31:54 AM'
        affecting_ticket_2_creation_date = '9/25/2020 8:31:54 AM'

        affecting_ticket_1 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_ticket_2 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_2_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_2_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_tickets_response = {
            'body': [
                affecting_ticket_1,
                affecting_ticket_2,
            ],
            'status': 200,
        }

        affecting_ticket_1_detail = {
            "detailID": 5217537,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_1_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Latency\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_1_details_object = {
            'ticketDetails': [
                affecting_ticket_1_detail,
            ],
            'ticketNotes': affecting_ticket_1_notes,
        }

        affecting_ticket_2_detail = {
            "detailID": 5217666,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_2_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Packet Loss\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_2_details_object = {
            'ticketDetails': [
                affecting_ticket_2_detail,
            ],
            'ticketNotes': affecting_ticket_2_notes,
        }

        ticket_details_response_1 = {
            'body': affecting_ticket_1_details_object,
            'status': 200,
        }
        ticket_details_response_2 = {
            'body': affecting_ticket_2_details_object,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            ticket_details_response_1,
            ticket_details_response_2,
        ])
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock(return_value=True)
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock(return_value=False)
        service_affecting_monitor._is_ticket_resolved = Mock()
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_has_calls([
            call(affecting_ticket_1),
            call(affecting_ticket_2),
        ])
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(affecting_ticket_1_id),
            call(affecting_ticket_2_id),
        ])
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_has_calls([
            call(affecting_ticket_1_notes, affecting_ticket_1_creation_date),
            call(affecting_ticket_2_notes, affecting_ticket_2_creation_date),
        ])
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_has_calls([
            call(affecting_ticket_1_notes),
            call(affecting_ticket_2_notes),
        ])
        service_affecting_monitor._is_ticket_resolved.assert_not_called()
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_affecting_ticket_details_being_resolved_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_ticket_1_id = 12345
        affecting_ticket_2_id = 67890

        affecting_ticket_1_creation_date = '9/25/2020 6:31:54 AM'
        affecting_ticket_2_creation_date = '9/25/2020 8:31:54 AM'

        affecting_ticket_1 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_ticket_2 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_2_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_2_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_tickets_response = {
            'body': [
                affecting_ticket_1,
                affecting_ticket_2,
            ],
            'status': 200,
        }

        affecting_ticket_1_detail = {
            "detailID": 5217537,
            "detailValue": serial_number,
            "detailStatus": "R",
        }
        affecting_ticket_1_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Latency\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_1_details_object = {
            'ticketDetails': [
                affecting_ticket_1_detail,
            ],
            'ticketNotes': affecting_ticket_1_notes,
        }

        affecting_ticket_2_detail = {
            "detailID": 5217666,
            "detailValue": serial_number,
            "detailStatus": "R",
        }
        affecting_ticket_2_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Packet Loss\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_2_details_object = {
            'ticketDetails': [
                affecting_ticket_2_detail,
            ],
            'ticketNotes': affecting_ticket_2_notes,
        }

        ticket_details_response_1 = {
            'body': affecting_ticket_1_details_object,
            'status': 200,
        }
        ticket_details_response_2 = {
            'body': affecting_ticket_2_details_object,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            ticket_details_response_1,
            ticket_details_response_2,
        ])
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock(return_value=True)
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock(return_value=True)
        service_affecting_monitor._is_ticket_resolved = Mock(return_value=True)
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_has_calls([
            call(affecting_ticket_1),
            call(affecting_ticket_2),
        ])
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(affecting_ticket_1_id),
            call(affecting_ticket_2_id),
        ])
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_has_calls([
            call(affecting_ticket_1_notes, affecting_ticket_1_creation_date),
            call(affecting_ticket_2_notes, affecting_ticket_2_creation_date),
        ])
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_has_calls([
            call(affecting_ticket_1_notes),
            call(affecting_ticket_2_notes),
        ])
        service_affecting_monitor._is_ticket_resolved.assert_has_calls([
            call(affecting_ticket_1_detail),
            call(affecting_ticket_2_detail),
        ])
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_environment_other_than_production_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_ticket_1_id = 12345
        affecting_ticket_2_id = 67890

        affecting_ticket_1_creation_date = '9/25/2020 6:31:54 AM'
        affecting_ticket_2_creation_date = '9/25/2020 8:31:54 AM'

        affecting_ticket_1 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_ticket_2 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_2_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_2_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_tickets_response = {
            'body': [
                affecting_ticket_1,
                affecting_ticket_2,
            ],
            'status': 200,
        }

        affecting_ticket_1_detail = {
            "detailID": 5217537,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_1_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Latency\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_1_details_object = {
            'ticketDetails': [
                affecting_ticket_1_detail,
            ],
            'ticketNotes': affecting_ticket_1_notes,
        }

        affecting_ticket_2_detail = {
            "detailID": 5217666,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_2_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Packet Loss\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_2_details_object = {
            'ticketDetails': [
                affecting_ticket_2_detail,
            ],
            'ticketNotes': affecting_ticket_2_notes,
        }

        ticket_details_response_1 = {
            'body': affecting_ticket_1_details_object,
            'status': 200,
        }
        ticket_details_response_2 = {
            'body': affecting_ticket_2_details_object,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            ticket_details_response_1,
            ticket_details_response_2,
        ])
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock(return_value=True)
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock(return_value=True)
        service_affecting_monitor._is_ticket_resolved = Mock(return_value=False)
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config["environment"] = 'dev'
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_has_calls([
            call(affecting_ticket_1),
            call(affecting_ticket_2),
        ])
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(affecting_ticket_1_id),
            call(affecting_ticket_2_id),
        ])
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_has_calls([
            call(affecting_ticket_1_notes, affecting_ticket_1_creation_date),
            call(affecting_ticket_2_notes, affecting_ticket_2_creation_date),
        ])
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_has_calls([
            call(affecting_ticket_1_notes),
            call(affecting_ticket_2_notes),
        ])
        service_affecting_monitor._is_ticket_resolved.assert_has_calls([
            call(affecting_ticket_1_detail),
            call(affecting_ticket_2_detail),
        ])
        bruin_repository.unpause_ticket_detail.assert_not_awaited()
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_with_unsuccessful_ticket_resolution_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_ticket_1_id = 12345
        affecting_ticket_2_id = 67890

        affecting_ticket_1_creation_date = '9/25/2020 6:31:54 AM'
        affecting_ticket_2_creation_date = '9/25/2020 8:31:54 AM'

        affecting_ticket_1 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_ticket_2 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_2_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_2_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_tickets_response = {
            'body': [
                affecting_ticket_1,
                affecting_ticket_2,
            ],
            'status': 200,
        }

        affecting_ticket_1_detail_id = 5217537
        affecting_ticket_1_detail = {
            "detailID": affecting_ticket_1_detail_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_1_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Latency\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_1_details_object = {
            'ticketDetails': [
                affecting_ticket_1_detail,
            ],
            'ticketNotes': affecting_ticket_1_notes,
        }

        affecting_ticket_2_detail_id = 5217666
        affecting_ticket_2_detail = {
            "detailID": affecting_ticket_2_detail_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_2_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Packet Loss\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_2_details_object = {
            'ticketDetails': [
                affecting_ticket_2_detail,
            ],
            'ticketNotes': affecting_ticket_2_notes,
        }

        ticket_details_response_1 = {
            'body': affecting_ticket_1_details_object,
            'status': 200,
        }
        ticket_details_response_2 = {
            'body': affecting_ticket_2_details_object,
            'status': 200,
        }

        resolve_ticket_detail_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            ticket_details_response_1,
            ticket_details_response_2,
        ])
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_ticket_detail_response)
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock(return_value=True)
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock(return_value=True)
        service_affecting_monitor._is_ticket_resolved = Mock(return_value=False)
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config["environment"] = 'production'
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_has_calls([
            call(affecting_ticket_1),
            call(affecting_ticket_2),
        ])
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(affecting_ticket_1_id),
            call(affecting_ticket_2_id),
        ])
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_has_calls([
            call(affecting_ticket_1_notes, affecting_ticket_1_creation_date),
            call(affecting_ticket_2_notes, affecting_ticket_2_creation_date),
        ])
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_has_calls([
            call(affecting_ticket_1_notes),
            call(affecting_ticket_2_notes),
        ])
        service_affecting_monitor._is_ticket_resolved.assert_has_calls([
            call(affecting_ticket_1_detail),
            call(affecting_ticket_2_detail),
        ])
        bruin_repository.unpause_ticket_detail.assert_has_awaits([
            call(affecting_ticket_1_id, serial_number),
            call(affecting_ticket_2_id, serial_number),
        ])
        bruin_repository.resolve_ticket.assert_has_awaits([
            call(affecting_ticket_1_id, affecting_ticket_1_detail_id),
            call(affecting_ticket_2_id, affecting_ticket_2_detail_id),
        ])
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        service_affecting_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_autoresolve_for_edge_ok_test(self):
        serial_number = 'VC1234567'
        client_id = 30000

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        affecting_ticket_1_id = 12345
        affecting_ticket_2_id = 67890

        affecting_ticket_1_creation_date = '9/25/2020 6:31:54 AM'
        affecting_ticket_2_creation_date = '9/25/2020 8:31:54 AM'

        affecting_ticket_1 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_1_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_ticket_2 = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": affecting_ticket_2_id,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": affecting_ticket_2_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        affecting_tickets_response = {
            'body': [
                affecting_ticket_1,
                affecting_ticket_2,
            ],
            'status': 200,
        }

        affecting_ticket_1_detail_id = 5217537
        affecting_ticket_1_detail = {
            "detailID": affecting_ticket_1_detail_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_1_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Latency\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_1_details_object = {
            'ticketDetails': [
                affecting_ticket_1_detail,
            ],
            'ticketNotes': affecting_ticket_1_notes,
        }

        affecting_ticket_2_detail_id = 5217666
        affecting_ticket_2_detail = {
            "detailID": affecting_ticket_2_detail_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }
        affecting_ticket_2_notes = [
            {
                "noteValue": (
                    "#*MetTel's IPA*#\n"
                    "Trouble: Packet Loss\n"
                    "TimeStamp: 2019-09-10 10:34:00-04:00"
                ),
                'createdDate': '2019-09-10 10:34:00-04:00',
                'serviceNumber': [
                    serial_number,
                ],
            }
        ]
        affecting_ticket_2_details_object = {
            'ticketDetails': [
                affecting_ticket_2_detail,
            ],
            'ticketNotes': affecting_ticket_2_notes,
        }

        ticket_details_response_1 = {
            'body': affecting_ticket_1_details_object,
            'status': 200,
        }
        ticket_details_response_2 = {
            'body': affecting_ticket_2_details_object,
            'status': 200,
        }

        resolve_ticket_detail_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_affecting_tickets = CoroutineMock(return_value=affecting_tickets_response)
        bruin_repository.get_ticket_details = CoroutineMock(side_effect=[
            ticket_details_response_1,
            ticket_details_response_2,
        ])
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_ticket_detail_response)
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._are_all_metrics_within_thresholds = Mock(return_value=True)
        service_affecting_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        service_affecting_monitor._was_last_affecting_trouble_detected_recently = Mock(return_value=True)
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable = Mock(return_value=True)
        service_affecting_monitor._is_ticket_resolved = Mock(return_value=False)
        service_affecting_monitor._notify_successful_autoresolve = CoroutineMock()

        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config["environment"] = 'production'
        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._run_autoresolve_for_edge(edge)

        service_affecting_monitor._are_all_metrics_within_thresholds.assert_called_once_with(edge)
        bruin_repository.get_open_affecting_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        service_affecting_monitor._was_ticket_created_by_automation_engine.assert_has_calls([
            call(affecting_ticket_1),
            call(affecting_ticket_2),
        ])
        bruin_repository.get_ticket_details.assert_has_awaits([
            call(affecting_ticket_1_id),
            call(affecting_ticket_2_id),
        ])
        service_affecting_monitor._was_last_affecting_trouble_detected_recently.assert_has_calls([
            call(affecting_ticket_1_notes, affecting_ticket_1_creation_date),
            call(affecting_ticket_2_notes, affecting_ticket_2_creation_date),
        ])
        service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable.assert_has_calls([
            call(affecting_ticket_1_notes),
            call(affecting_ticket_2_notes),
        ])
        service_affecting_monitor._is_ticket_resolved.assert_has_calls([
            call(affecting_ticket_1_detail),
            call(affecting_ticket_2_detail),
        ])
        bruin_repository.unpause_ticket_detail.assert_has_awaits([
            call(affecting_ticket_1_id, serial_number),
            call(affecting_ticket_2_id, serial_number),
        ])
        bruin_repository.resolve_ticket.assert_has_awaits([
            call(affecting_ticket_1_id, affecting_ticket_1_detail_id),
            call(affecting_ticket_2_id, affecting_ticket_2_detail_id),
        ])
        bruin_repository.append_autoresolve_note_to_ticket.assert_has_awaits([
            call(affecting_ticket_1_id, serial_number),
            call(affecting_ticket_2_id, serial_number),
        ])
        service_affecting_monitor._notify_successful_autoresolve.assert_has_awaits([
            call(affecting_ticket_1_id, serial_number),
            call(affecting_ticket_2_id, serial_number),
        ])

    def group_links_by_edge_test(self):
        contact_info = {
            'ticket': {
                'email': 'fake@mail.com',
                'phone': '6666666666',
                'name': 'Fake'
            },
            'site': {
                'email': 'fake@mail.com',
                'phone': '6666666666',
                'name': 'Fake'
            },
        }

        edge_1_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            # Some fields omitted for simplicity
        }
        edge_2_status = {
            'host': 'metvco02.mettel.net',
            'enterpriseName': 'Diamond Dogs',
            'enterpriseId': 1,
            'edgeName': 'Naked Snake',
            'edgeState': 'CONNECTED',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC7654321',
            # Some fields omitted for simplicity
        }

        edge_1_cached_info = {
            'edge': {
                'host': 'mettel.velocloud.net',
                'enterprise_id': 1,
                'edge_id': 1,
            },
            'serial_number': 'VC1234567',
            'bruin_client_info': {
                'client_id': 30000,
                'client_name': 'MetTel',
            },
            # Some fields omitted for simplicity
        }
        edge_2_cached_info = {
            'edge': {
                'host': 'metvco02.mettel.net',
                'enterprise_id': 1,
                'edge_id': 1,
            },
            'serial_number': 'VC7654321',
            'bruin_client_info': {
                'client_id': 30000,
                'client_name': 'MetTel',
            },
            # Some fields omitted for simplicity
        }

        link_1_status = {
            'displayName': '70.59.5.185',
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
            # Some fields omitted for simplicity
        }
        link_1_metrics = {
            'bytesTx': 5694196,
            'bytesRx': 9607567,
            'bpsOfBestPathRx': 182296000,
            'bpsOfBestPathTx': 43243000,
            'bestJitterMsRx': 0,
            'bestJitterMsTx': 0,
            'bestLatencyMsRx': 3,
            'bestLatencyMsTx': 6.4167,
            'bestLossPctRx': 0,
            'bestLossPctTx': 0,
            # Some fields omitted for simplicity
        }

        link_2_status = {
            'displayName': '70.59.5.186',
            'interface': 'RAY',
            'linkState': 'STABLE',
            'linkId': 5294,
            # Some fields omitted for simplicity
        }
        link_2_metrics = {
            'bytesTx': 5694197,
            'bytesRx': 9607568,
            'bpsOfBestPathRx': 182296001,
            'bpsOfBestPathTx': 43243001,
            'bestJitterMsRx': 1,
            'bestJitterMsTx': 1,
            'bestLatencyMsRx': 4,
            'bestLatencyMsTx': 6.4168,
            'bestLossPctRx': 1,
            'bestLossPctTx': 1,
            # Some fields omitted for simplicity
        }

        link_3_status = {
            'displayName': '70.59.5.187',
            'interface': 'ZEKE',
            'linkState': 'STABLE',
            'linkId': 5295,
            # Some fields omitted for simplicity
        }
        link_3_metrics = {
            'bytesTx': 5694198,
            'bytesRx': 9607569,
            'bpsOfBestPathRx': 182296002,
            'bpsOfBestPathTx': 43243002,
            'bestJitterMsRx': 2,
            'bestJitterMsTx': 2,
            'bestLatencyMsRx': 5,
            'bestLatencyMsTx': 6.4169,
            'bestLossPctRx': 2,
            'bestLossPctTx': 2,
            # Some fields omitted for simplicity
        }

        link_1_metrics_with_cache_and_contact_info = {
            'cached_info': edge_1_cached_info,
            'contact_info': contact_info,
            'edge_status': edge_1_status,
            'link_status': link_1_status,
            'link_metrics': link_1_metrics,
        }
        link_2_metrics_with_cache_and_contact_info = {
            'cached_info': edge_1_cached_info,
            'contact_info': contact_info,
            'edge_status': edge_1_status,
            'link_status': link_2_status,
            'link_metrics': link_2_metrics,
        }
        link_3_metrics_with_cache_and_contact_info = {
            'cached_info': edge_2_cached_info,
            'contact_info': contact_info,
            'edge_status': edge_2_status,
            'link_status': link_3_status,
            'link_metrics': link_3_metrics,
        }
        links_metrics_with_cache_and_contact_info = [
            link_1_metrics_with_cache_and_contact_info,
            link_2_metrics_with_cache_and_contact_info,
            link_3_metrics_with_cache_and_contact_info,
        ]

        edge_1_with_links_info = {
            'cached_info': edge_1_cached_info,
            'contact_info': contact_info,
            'edge_status': edge_1_status,
            'links': [
                {
                    'link_status': link_1_status,
                    'link_metrics': link_1_metrics,
                },
                {
                    'link_status': link_2_status,
                    'link_metrics': link_2_metrics,
                },
            ]
        }
        edge_2_with_links_info = {
            'cached_info': edge_2_cached_info,
            'contact_info': contact_info,
            'edge_status': edge_2_status,
            'links': [
                {
                    'link_status': link_3_status,
                    'link_metrics': link_3_metrics,
                },
            ]
        }
        edges_with_links_info = [
            edge_1_with_links_info,
            edge_2_with_links_info,
        ]

        result = ServiceAffectingMonitor._group_links_by_edge(links_metrics_with_cache_and_contact_info)
        assert result == edges_with_links_info

    def are_all_metrics_within_thresholds_with_all_metrics_ok_and_client_being_RSI_test(self):
        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': 'VC1234567',
                'bruin_client_info': {
                    'client_id': 83109,
                    'client_name': 'RSI',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        result = service_affecting_monitor._are_all_metrics_within_thresholds(edge)
        assert result is True

    def are_all_metrics_within_thresholds_with_some_metrics_above_threshold_and_client_being_RSI_test(self):
        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': 'VC1234567',
                'bruin_client_info': {
                    'client_id': 83109,
                    'client_name': 'RSI',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 200,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 200,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 20,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 205,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 205,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 25,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        result = service_affecting_monitor._are_all_metrics_within_thresholds(edge)
        assert result is False

    def are_all_metrics_within_thresholds_with_all_metrics_ok_and_client_not_being_RSI_test(self):
        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': 'VC1234567',
                'bruin_client_info': {
                    'client_id': 30000,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        result = service_affecting_monitor._are_all_metrics_within_thresholds(edge)
        assert result is True

    def are_all_metrics_within_thresholds_with_some_metrics_above_threshold_and_client_not_being_RSI_test(self):
        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': 'VC1234567',
                'bruin_client_info': {
                    'client_id': 30000,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500,
                        'bytesRx': 500,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 200,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 200,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 20,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600,
                        'bytesRx': 600,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 205,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 205,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 25,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        result = service_affecting_monitor._are_all_metrics_within_thresholds(edge)
        assert result is False

    def are_all_metrics_within_thresholds_with_only_bandwidth_metrics_above_threshold_and_client_not_being_RSI_test(
            self):
        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1,
                },
                'serial_number': 'VC1234567',
                'bruin_client_info': {
                    'client_id': 30000,
                    'client_name': 'MetTel',
                },
                # Some fields omitted for simplicity
            },
            'links': [
                {
                    'link_metrics': {
                        'bytesTx': 500000,
                        'bytesRx': 500000,
                        'bpsOfBestPathRx': 100,
                        'bpsOfBestPathTx': 100,
                        'bestJitterMsRx': 30,
                        'bestJitterMsTx': 30,
                        'bestLatencyMsRx': 100,
                        'bestLatencyMsTx': 100,
                        'bestLossPctRx': 5,
                        'bestLossPctTx': 5,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
                {
                    'link_metrics': {
                        'bytesTx': 600000,
                        'bytesRx': 600000,
                        'bpsOfBestPathRx': 150,
                        'bpsOfBestPathTx': 150,
                        'bestJitterMsRx': 35,
                        'bestJitterMsTx': 35,
                        'bestLatencyMsRx': 105,
                        'bestLatencyMsTx': 105,
                        'bestLossPctRx': 2,
                        'bestLossPctTx': 2,
                        # Some fields omitted for simplicity
                    },
                    # Some fields omitted for simplicity
                },
            ]
            # Some fields omitted for simplicity
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        result = service_affecting_monitor._are_all_metrics_within_thresholds(edge)
        assert result is True

    def was_ticket_created_by_automation_engine_test(self):
        ticket = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": 12345,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "Intelygenz Ai",
        }
        result = ServiceAffectingMonitor._was_ticket_created_by_automation_engine(ticket)
        assert result is True

        ticket = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": 12345,
            "category": "SD-WAN",
            "topic": "Service Affecting Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "InterMapper Service",
        }
        result = ServiceAffectingMonitor._was_ticket_created_by_automation_engine(ticket)
        assert result is False

    def is_affecting_ticket_detail_auto_resolvable_test(self):
        serial_number = 'VC1234567'

        text_identifier = (
            "#*MetTel's IPA*#\n"
            f"Auto-resolving task for serial {serial_number}\n"
        )

        autoresolve_note_text = f"{text_identifier}TimeStamp: 2021-01-02 10:18:16-05:00"

        non_autoresolve_note_text = (
            "#*MetTel's IPA*#\n"
            "Just another kind of note\n"
        )

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        ticket_notes = [
            {
                "noteId": 41894040,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": non_autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
        ]
        result = service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable(ticket_notes)
        assert result is True

        ticket_notes = [
            {
                "noteId": 41894040,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
            {
                "noteId": 41894041,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": non_autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
        ]
        result = service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable(ticket_notes)
        assert result is True

        ticket_notes = [
            {
                "noteId": 41894040,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
            {
                "noteId": 41894041,
                "noteValue": non_autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            }
        ]
        result = service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable(ticket_notes)
        assert result is False

        ticket_notes = [
            {
                "noteId": 41894040,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": autoresolve_note_text,
                "serviceNumber": [
                    serial_number,
                ],
            }
        ]
        result = service_affecting_monitor._is_affecting_ticket_detail_auto_resolvable(ticket_notes)
        assert result is False

    def was_last_affecting_trouble_detected_recently_with_none_of_reopen_note_and_initial_affecting_note_found_test(
            self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        ticket_notes = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, minutes=14, seconds=59)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, minutes=15)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, minutes=15, seconds=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is False

    def was_last_affecting_trouble_detected_recently_with_reopen_note_found_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        initial_affecting_note_timestamp = '2021-01-02T10:18:16.71-05:00'
        reopen_timestamp = '2021-01-02T11:00:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nEdge Name: Big Boss\nTrouble: Jitter\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": initial_affecting_note_timestamp,
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nRe-opening\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": reopen_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(hours=1, minutes=14, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, minutes=15)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, minutes=15, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is False

    def was_last_affecting_trouble_detected_recently_with_reopen_note_not_found_and_initial_affecting_note_found_test(
            self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        initial_affecting_note_timestamp = '2021-01-02T10:18:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nEdge Name: Big Boss\nTrouble: Jitter\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": initial_affecting_note_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        datetime_mock = Mock()

        new_now = parse(initial_affecting_note_timestamp) + timedelta(hours=1, minutes=14, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is True

        new_now = parse(initial_affecting_note_timestamp) + timedelta(hours=1, minutes=15)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is True

        new_now = parse(initial_affecting_note_timestamp) + timedelta(hours=1, minutes=15, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            result = service_affecting_monitor._was_last_affecting_trouble_detected_recently(
                ticket_notes, ticket_creation_date
            )
            assert result is False

    def get_first_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = ServiceAffectingMonitor._get_first_element_matching(iterable=payload, condition=cond)
        expected = 5

        assert result == expected

    def get_first_element_matching_with_no_match_test(self):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = ServiceAffectingMonitor._get_first_element_matching(
            iterable=payload, condition=cond, fallback=fallback_value
        )

        assert result == fallback_value

    def get_last_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        result = service_affecting_monitor._get_last_element_matching(iterable=payload, condition=cond)
        expected = 10

        assert result == expected

    def get_last_element_matching_with_no_match_test(self):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        result = service_affecting_monitor._get_last_element_matching(
            iterable=payload, condition=cond, fallback=fallback_value
        )

        assert result == fallback_value

    @pytest.mark.asyncio
    async def notify_successful_autoresolve_test(self):
        ticket_id = 12345
        serial_number = 'VC1234567'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        await service_affecting_monitor._notify_successful_autoresolve(ticket_id, serial_number)

        autoresolve_slack_message = (
            f'Task related to serial number {serial_number} in Service Affecting ticket {ticket_id} was autoresolved. '
            f'Details at https://app.bruin.com/t/{ticket_id}'
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(autoresolve_slack_message)

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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "R"}],
            "ticketNotes": [
                {
                    "noteValue": "#*MetTel's IPA*# \n "
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
        service_affecting_monitor._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened = Mock()
        service_affecting_monitor._schedule_forward_to_hnoc_queue = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._ticket_object_to_string_without_watermark.assert_called_once()
        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once_with(
            ticket_mock['ticketID'], ticket_mock['ticketDetails'][0]['detailID'])
        service_affecting_monitor._notifications_repository.send_slack_message. \
            assert_awaited_once_with(slack_message_mock)
        service_affecting_monitor._metrics_repository.increment_tickets_reopened.assert_called_once()
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_called_once_with(
            ticket_id=ticket_mock['ticketID'], serial_number=link_info['cached_info']['serial_number']
        )

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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": '', "detailStatus": "R"}],
            "ticketNotes": [
                {
                    "noteValue": "#*MetTel's IPA*# \n "
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
        service_affecting_monitor._bruin_repository._notifications_repository.send_slack_message. \
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "O"}],
            "ticketNotes": [
                {
                    "noteValue": "#*MetTel's IPA*# \n "
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
                        f'https://app.bruin.com/helpdesk?clientId=85940&' \
                        f'ticketId=3521039 , in ' \
                        f'production'
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._ticket_object_to_string_without_watermark = Mock()
        service_affecting_monitor._bruin_repository.open_ticket = CoroutineMock(side_effect=[open_ticket_response_mock])
        service_affecting_monitor._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        service_affecting_monitor._metrics_repository.increment_tickets_reopened = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._notify_trouble(link_info, 'JITTER', ticket_dict)

        bruin_repository.append_note_to_ticket.assert_awaited_once()
        notifications_repository.send_slack_message.assert_awaited_once()
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "O"}],
            "ticketNotes": [
                {
                    "noteValue": "#*MetTel's IPA*# \n "
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "R"}],
            "ticketNotes": [
                {
                    "noteValue": "#*MetTel's IPA*# \n "
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
        service_affecting_monitor._bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        service_affecting_monitor._notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._ticket_object_to_string.assert_not_called()
        service_affecting_monitor._bruin_repository.open_ticket.assert_awaited_once_with(
            ticket_mock['ticketID'], ticket_mock['ticketDetails'][0]['detailID'])
        service_affecting_monitor._notifications_repository.send_slack_message. \
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = None
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._ticket_object_to_string = Mock()

        await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._ticket_object_to_string.assert_not_called()

    @pytest.mark.asyncio
    async def notify_trouble_with_none_affecting_ticket_and_production_environment_test(self):
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = None
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._ticket_object_to_string = Mock(return_value='Some string object')

        await service_affecting_monitor._notify_trouble(link_info, trouble, ticket_dict)

        bruin_repository.get_affecting_ticket.assert_awaited_once_with(
            client_id, "VC05200028729")

        service_affecting_monitor._ticket_object_to_string.assert_not_called()
        event_bus.rpc_request.assert_not_awaited()
        metrics_repository.increment_tickets_created.assert_not_called()

    @pytest.mark.asyncio
    async def notify_trouble_with_no_existing_ticket_and_production_environment_failed_rpc_test(self):
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        metrics_repository = Mock()
        metrics_repository.increment_tickets_created = Mock()
        bruin_repository = Mock()

        event_bus = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock(side_effect=[{'body': 'Failed', 'status': 400},
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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

        uuid_ = uuid()

        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = {}
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._ticket_object_to_string = Mock(return_value='Some string object')

        await service_affecting_monitor._notify_trouble(link_info, trouble, ticket_dict)

        bruin_repository.get_affecting_ticket.assert_awaited_once_with(
            client_id, "VC05200028729")

        service_affecting_monitor._ticket_object_to_string.assert_called_once()
        metrics_repository.increment_tickets_created.assert_not_called()

    @pytest.mark.asyncio
    async def notify_trouble_pro_ticket_not_exists_success_rpc_test(self):
        serial_number = 'VC05200028729'

        event_bus = Mock()

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
                "serialNumber": serial_number,
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        ticket_id = 123
        trouble = 'LATENCY'

        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        bruin_repository.create_affecting_ticket = CoroutineMock(side_effect=[{'body': {'ticketIds': [ticket_id]},
                                                                               'status': 200},
                                                                              'Note Posted',
                                                                              'Slack Sent'])
        bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=[{'body': {'ticketIds': [123]},
                                                                             'status': 200},
                                                                            'Note Posted',
                                                                            'Slack Sent'])

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_mock = {}
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._ticket_object_to_string = Mock(return_value='Some string object')
        service_affecting_monitor._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor._schedule_forward_to_hnoc_queue = Mock()

        await service_affecting_monitor._notify_trouble(link_info, trouble, ticket_dict)

        bruin_repository.get_affecting_ticket.assert_awaited_once_with(
            client_id, serial_number
        )
        service_affecting_monitor._ticket_object_to_string.assert_called_with(ticket_dict)

        metrics_repository.increment_tickets_created.assert_called_once()
        assert bruin_repository.create_affecting_ticket.called
        service_affecting_monitor._schedule_forward_to_hnoc_queue.assert_called_once_with(
            ticket_id=ticket_id, serial_number=serial_number
        )
        assert 'Some string object' == bruin_repository.append_note_to_ticket.mock_calls[0][2]['note']

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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1'
            },
            'link_metrics': {
                'bestLatencyMsRx': 14,
                'bestLatencyMsTx': 20,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        config.MONITOR_CONFIG['environment'] = 'some-unknown-config'
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._template_renderer.compose_email_object = Mock(return_value='Some email object')

        await service_affecting_monitor._notify_trouble(link_info, 'LATENCY', ticket_dict)

        service_affecting_monitor._template_renderer.compose_email_object.assert_not_called()
        event_bus.rpc_request.assert_not_awaited()

    @pytest.mark.asyncio
    async def schedule_forward_to_hnoc_queue_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        current_datetime = datetime.now()
        forward_task_run_date = current_datetime + timedelta(seconds=config.MONITOR_CONFIG['forward_to_hnoc'])

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(service_affecting_monitor_module, 'timezone', new=Mock()):
                service_affecting_monitor._schedule_forward_to_hnoc_queue(
                    ticket_id=ticket_id, serial_number=serial_number
                )

        scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._forward_ticket_to_hnoc_queue, 'date',
            kwargs={'ticket_id': ticket_id, 'serial_number': serial_number},
            run_date=forward_task_run_date,
            replace_existing=False,
            id=f'_forward_ticket_{ticket_id}_{serial_number}_to_hnoc',
        )

    @pytest.mark.asyncio
    async def forward_ticket_to_hnoc_queue_ok_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345

        change_work_queue_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        velocloud_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.change_detail_work_queue_to_hnoc = CoroutineMock(return_value=change_work_queue_response)

        notifications_repository = Mock()
        notifications_repository.notify_successful_ticket_forward = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        await service_affecting_monitor._forward_ticket_to_hnoc_queue(ticket_id=ticket_id, serial_number=serial_number)

        bruin_repository.change_detail_work_queue_to_hnoc.assert_awaited_once_with(
            ticket_id=ticket_id, service_number=serial_number,
        )
        notifications_repository.notify_successful_ticket_forward.assert_awaited_once_with(
            ticket_id=ticket_id, serial_number=serial_number,
        )

    @pytest.mark.asyncio
    async def forward_ticket_to_hnoc_queue_with_change_work_queue_rpc_having_non_2xx_status_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345

        change_work_queue_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        velocloud_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.change_detail_work_queue_to_hnoc = CoroutineMock(return_value=change_work_queue_response)

        notifications_repository = Mock()
        notifications_repository.notify_successful_ticket_forward = CoroutineMock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)

        await service_affecting_monitor._forward_ticket_to_hnoc_queue(ticket_id=ticket_id, serial_number=serial_number)

        bruin_repository.change_detail_work_queue_to_hnoc.assert_awaited_once_with(
            ticket_id=ticket_id, service_number=serial_number,
        )
        notifications_repository.notify_successful_ticket_forward.assert_not_awaited()

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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1',
                'displayName': 'Test'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_1_best_latency_ms_rx,
                'bestLatencyMsTx': link_1_best_latency_ms_tx,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1',
                'displayName': 'Test'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_2_best_latency_ms_rx,
                'bestLatencyMsTx': link_2_best_latency_ms_tx,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
                "enterprise_name": "Titan America|85940|"
            },
            'link_status': {
                'interface': 'GE1',
                'displayName': 'Test'
            },
            'link_metrics': {
                'bestLatencyMsRx': link_3_best_latency_ms_rx,
                'bestLatencyMsTx': link_3_best_latency_ms_tx,
            },
            'cached_info': {
                'edge': {
                    "host": "mettel.velocloud.net",
                    "enterprise_id": 137,
                    "edge_id": 1651
                },
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        ticket_note = service_affecting_monitor._ticket_object_to_string(test_dict)
        assert ticket_note == "#*MetTel's IPA*# \nEdgeName: Test \nEdge Status: ok \n"

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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        notifications_repository = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
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
        notifications_repository = Mock()
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
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._customer_cache = customer_cache_repository
        map_cached_edges_with_links_metrics = service_affecting_monitor. \
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

        notifications_repository = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer,
                                                            metrics_repository, bruin_repository, velocloud_repository,
                                                            customer_cache_repository, notifications_repository)
        service_affecting_monitor._ticket_object_to_string = Mock()

        service_affecting_monitor._ticket_object_to_string_without_watermark(ticket_dict)

        service_affecting_monitor._ticket_object_to_string.assert_called_once_with(ticket_dict, "")
