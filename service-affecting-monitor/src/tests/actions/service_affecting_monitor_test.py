from collections import OrderedDict
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from apscheduler.util import undefined
from asynctest import CoroutineMock

from application.actions import service_affecting_monitor as service_affecting_monitor_module
from config import testconfig


class TestServiceAffectingMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)

        assert service_affecting_monitor._event_bus is event_bus
        assert service_affecting_monitor._logger is logger
        assert service_affecting_monitor._scheduler is scheduler
        assert service_affecting_monitor._config is config

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(service_affecting_monitor_module, 'timezone', new=Mock()):
                await service_affecting_monitor.start_service_affecting_monitor_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._monitor_each_edge, 'interval',
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes"],
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

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        await service_affecting_monitor.start_service_affecting_monitor_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_affecting_monitor._monitor_each_edge, 'interval',
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes"],
            next_run_time=undefined,
            replace_existing=True,
            id='_monitor_each_edge',
        )

    @pytest.mark.asyncio
    async def service_affecting_monitor_process_test(self):
        logger = Mock()
        scheduler = Mock()
        config = testconfig

        device = {
                  "host": "mettel.velocloud.net",
                  "enterprise_id": 137,
                  "edge_id": 1602
                }

        link_1 = {
            'bestLatencyMsRx': 14,
            'bestLatencyMsTx': 121,
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        link_2 = {
            'bestLatencyMsRx': 60,
            'bestLatencyMsTx': 20,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link_1, link_2]
            }
        }
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=edges_to_report)
        template_renderer = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._latency_check = CoroutineMock()
        service_affecting_monitor._packet_loss_check = CoroutineMock()

        await service_affecting_monitor._service_affecting_monitor_process(device)

        event_bus.rpc_request.assert_awaited_once()
        service_affecting_monitor._latency_check.assert_has_awaits([
            call(device, edges_to_report, link_1),
            call(device, edges_to_report, link_2)
        ], any_order=True)
        service_affecting_monitor._packet_loss_check.assert_has_awaits([
            call(device, edges_to_report, link_1),
            call(device, edges_to_report, link_2)
        ], any_order=True)

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
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        link_2 = {
            'bestLatencyMsRx': link_2_best_latency_ms_rx,
            'bestLatencyMsTx': link_2_best_latency_ms_tx,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        link_3 = {
            'bestLatencyMsRx': link_3_best_latency_ms_rx,
            'bestLatencyMsTx': link_3_best_latency_ms_tx,
            'serviceGroups': ['PRIVATE_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link_1, link_2, link_3]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link_1)
        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link_2)
        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link_3)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check_with_wireless_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Latency'
        tx_wireless_threshold = 120
        link_best_latency_ms_rx = 14
        link_best_latency_ms_tx = 121

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_latency_ms_rx,
            link_best_latency_ms_tx, trouble_text, tx_wireless_threshold,
        )

    @pytest.mark.asyncio
    async def latency_check_with_wireless_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Latency'
        rx_wireless_threshold = 120
        link_best_latency_ms_rx = 121
        link_best_latency_ms_tx = 14

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_latency_ms_rx,
            link_best_latency_ms_tx, trouble_text, rx_wireless_threshold,
        )

    @pytest.mark.asyncio
    async def latency_check_with_wireless_link_and_both_tx_and_rx_values_below_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_latency_ms_rx = 115
        link_best_latency_ms_tx = 118

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check_with_public_wired_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Latency'
        tx_public_wired_threshold = 50
        link_best_latency_ms_rx = 14
        link_best_latency_ms_tx = 60

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_latency_ms_rx,
            link_best_latency_ms_tx, trouble_text, tx_public_wired_threshold,
        )

    @pytest.mark.asyncio
    async def latency_check_with_public_wired_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Latency'
        rx_public_wired_threshold = 50
        link_best_latency_ms_rx = 60
        link_best_latency_ms_tx = 14

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_latency_ms_rx,
            link_best_latency_ms_tx, trouble_text, rx_public_wired_threshold,
        )

    @pytest.mark.asyncio
    async def latency_check_with_public_wired_link_and_both_tx_and_rx_values_below_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_latency_ms_rx = 40
        link_best_latency_ms_tx = 45

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check_with_private_wired_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Latency'
        tx_private_wired_threshold = 50
        link_best_latency_ms_rx = 14
        link_best_latency_ms_tx = 60

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PRIVATE_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_latency_ms_rx,
            link_best_latency_ms_tx, trouble_text, tx_private_wired_threshold,
        )

    @pytest.mark.asyncio
    async def latency_check_with_private_wired_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Latency'
        rx_private_wired_threshold = 50
        link_best_latency_ms_rx = 60
        link_best_latency_ms_tx = 14

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PRIVATE_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 14,
                        'serviceGroups': ['None']
                    },
                    {
                        'bestLatencyMsRx': 49,
                        'bestLatencyMsTx': 20,
                        'serviceGroups': ['None']
                    },

                ]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_latency_ms_rx,
            link_best_latency_ms_tx, trouble_text, rx_private_wired_threshold,
        )

    @pytest.mark.asyncio
    async def latency_check_with_private_wired_link_and_both_tx_and_rx_values_below_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_latency_ms_rx = 40
        link_best_latency_ms_tx = 45

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['PRIVATE_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def latency_check_with_unknown_link_type_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_latency_ms_rx = 40
        link_best_latency_ms_tx = 45

        link = {
            'bestLatencyMsRx': link_best_latency_ms_rx,
            'bestLatencyMsTx': link_best_latency_ms_tx,
            'serviceGroups': ['UNKNOWN']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._latency_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check_with_no_troubles(self):
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
            'bestLatencyMsRx': link_1_best_loss_packets_rx,
            'bestLatencyMsTx': link_1_best_loss_packets_tx,
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        link_2 = {
            'bestLatencyMsRx': link_2_best_loss_packets_rx,
            'bestLatencyMsTx': link_2_best_loss_packets_tx,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        link_3 = {
            'bestLatencyMsRx': link_3_best_loss_packets_rx,
            'bestLatencyMsTx': link_3_best_loss_packets_tx,
            'serviceGroups': ['PRIVATE_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link_1, link_2, link_3]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link_1)
        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link_2)
        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link_3)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check_with_wireless_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Packet Loss'
        tx_wireless_threshold = 8
        link_best_loss_packets_rx = 7
        link_best_loss_packets_tx = 10

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_loss_packets_rx,
            link_best_loss_packets_tx, trouble_text, tx_wireless_threshold,
        )

    @pytest.mark.asyncio
    async def packet_loss_check_with_wireless_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Packet Loss'
        rx_wireless_threshold = 8
        link_best_loss_packets_rx = 10
        link_best_loss_packets_tx = 7

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_loss_packets_rx,
            link_best_loss_packets_tx, trouble_text, rx_wireless_threshold,
        )

    @pytest.mark.asyncio
    async def packet_loss_check_with_wireless_link_and_both_tx_and_rx_values_below_threshold_test(self):
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
        link_best_loss_packets_tx = 7

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PUBLIC_WIRELESS']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check_with_public_wired_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Packet Loss'
        tx_public_wired_threshold = 5
        link_best_loss_packets_rx = 4
        link_best_loss_packets_tx = 6

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_loss_packets_rx,
            link_best_loss_packets_tx, trouble_text, tx_public_wired_threshold,
        )

    @pytest.mark.asyncio
    async def packet_loss_check_with_public_wired_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Packet Loss'
        rx_public_wired_threshold = 5
        link_best_loss_packets_rx = 6
        link_best_loss_packets_tx = 4

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_loss_packets_rx,
            link_best_loss_packets_tx, trouble_text, rx_public_wired_threshold,
        )

    @pytest.mark.asyncio
    async def packet_loss_check_with_public_wired_link_and_both_tx_and_rx_values_below_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_loss_packets_rx = 1
        link_best_loss_packets_tx = 1

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PUBLIC_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check_with_private_wired_link_and_tx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Packet Loss'
        tx_private_wired_threshold = 5
        link_best_loss_packets_rx = 4
        link_best_loss_packets_tx = 6

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PRIVATE_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_loss_packets_rx,
            link_best_loss_packets_tx, trouble_text, tx_private_wired_threshold,
        )

    @pytest.mark.asyncio
    async def packet_loss_check_with_private_wired_link_and_rx_values_above_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        trouble_text = 'Packet Loss'
        rx_private_wired_threshold = 5
        link_best_loss_packets_rx = 6
        link_best_loss_packets_tx = 4

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PRIVATE_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_awaited_once_with(
            device, edges_to_report, link, link_best_loss_packets_rx,
            link_best_loss_packets_tx, trouble_text, rx_private_wired_threshold,
        )

    @pytest.mark.asyncio
    async def packet_loss_check_with_public_wired_link_and_both_tx_and_rx_values_below_threshold_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_loss_packets_rx = 1
        link_best_loss_packets_tx = 1

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['PRIVATE_WIRED']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def packet_loss_check_with_unknown_link_type_test(self):
        scheduler = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = testconfig

        device = {
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1602
        }

        link_best_loss_packets_rx = 6
        link_best_loss_packets_tx = 4

        link = {
            'bestLossPctRx': link_best_loss_packets_rx,
            'bestLossPctTx': link_best_loss_packets_tx,
            'serviceGroups': ['UNKNOWN']
        }
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [link]
            }
        }
        logger = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._notify_trouble = CoroutineMock()

        await service_affecting_monitor._packet_loss_check(device=device, edge_status=edges_to_report, link=link)

        service_affecting_monitor._notify_trouble.assert_not_awaited()

    @pytest.mark.asyncio
    async def notify_trouble_with_production_environment_exists_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[{'ticketIds': {'ticketIds': [123]}}, 'Note Posted',
                                                           'Slack Sent'])
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        device = {
            "serial": 'VC05200033383',
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "email": "fake@gmail.com",
            "phone": "111-111-1111",
            "name": "Fake Guy"
        }

        config = testconfig
        config.MONITOR_CONFIG["environment"] = 'production'

        client_id = '85940'
        trouble = 'LATENCY'
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE2",
                            "displayName": "Test2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._ticket_existence = CoroutineMock(return_value=True)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._ticket_object_to_string = Mock(return_value='Some string object')

        await service_affecting_monitor._notify_trouble(device, edges_to_report, 'Some Link Info', 'Input results',
                                                        'Output results', trouble, 120)

        service_affecting_monitor._ticket_existence.assert_awaited_once_with(client_id,
                                                                             edges_to_report['edge_info']['edges'][
                                                                                 'serialNumber'], trouble)

        service_affecting_monitor._compose_ticket_dict.assert_called_once()
        service_affecting_monitor._ticket_object_to_string.assert_not_called()
        event_bus.rpc_request.assert_not_called()

    @pytest.mark.asyncio
    async def _notify_trouble_pro_ticket_not_exists_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[{'ticketIds': {'ticketIds': [123]}}, 'Note Posted',
                                                           'Slack Sent'])
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        config.MONITOR_CONFIG['environment'] = 'production'
        device = {
            "serial": 'VC05200033383',
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "email": "fake@gmail.com",
            "phone": "111-111-1111",
            "name": "Fake Guy"
        }

        client_id = '85940'
        trouble = 'LATENCY'
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE2",
                            "displayName": "Test2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._ticket_existence = CoroutineMock(return_value=False)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._ticket_object_to_string = Mock(return_value='Some string object')

        await service_affecting_monitor._notify_trouble(device, edges_to_report, 'Some Link Info', 'Input results',
                                                        'Output results', trouble, 120)

        service_affecting_monitor._ticket_existence.assert_awaited_once_with(client_id,
                                                                             edges_to_report['edge_info']['edges'][
                                                                                 'serialNumber'], trouble)

        service_affecting_monitor._compose_ticket_dict.assert_called_once()
        service_affecting_monitor._ticket_object_to_string.assert_called_with('Some ordered dict object')

        assert event_bus.rpc_request.called
        assert 'Some string object' in event_bus.rpc_request.mock_calls[1][1][1]

    @pytest.mark.asyncio
    async def notify_trouble_with_unknown_config_test(self):
        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value="Email Sent")
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        device = {
            "serial": 'VC05200033383',
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "email": "fake@gmail.com",
            "phone": "111-111-1111",
            "name": "Fake Guy"
        }

        config = testconfig
        config.MONITOR_CONFIG['environment'] = None

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_affecting_monitor._compose_ticket_dict = Mock(return_value='Some ordered dict object')
        service_affecting_monitor._template_renderer.compose_email_object = Mock(return_value='Some email object')

        await service_affecting_monitor._notify_trouble(device, 'Some Edge Status', 'Some Link Info', 'Input results',
                                                        'Output results', 'LATENCY', 120)

        service_affecting_monitor._compose_ticket_dict.assert_called_once()
        service_affecting_monitor._template_renderer.compose_email_object.assert_not_called()
        event_bus.rpc_request.assert_not_awaited()

    @pytest.mark.asyncio
    async def ticket_existence_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        config = testconfig
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026138'}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*# \n '
                                                                           'Trouble: LATENCY\n '
                                                                           'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                                                              'createdDate': '2019-09-10 10:34:00-04:00'}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details])
        ticket_exists = await service_affecting_monitor._ticket_existence(85940, 'VC05200026138', 'LATENCY')
        assert ticket_exists is True
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def ticket_existence_wrong_trouble_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026138'}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*# \n '
                                                                           'Trouble: LATENCY\n '
                                                                           'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                                                              'createdDate': '2019-09-10 10:34:00-04:00'}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details, 'Slack Sent'])
        ticket_exists = await service_affecting_monitor._ticket_existence(85940, 'VC05200026138', 'PACKET_LOSS')
        assert ticket_exists is False
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def ticket_existence_wrong_serial_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026137'}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*# \n '
                                                                           'Trouble: LATENCY\n '
                                                                           'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                                                              'createdDate': '2019-09-10 10:34:00-04:00'}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details])
        ticket_exists = await service_affecting_monitor._ticket_existence(85940, 'VC05200026138', 'LATENCY')
        assert ticket_exists is False
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def ticket_existence_no_details_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{'otherDetails': None}],
                                             "ticketNotes": [{"noteValue": '#*Automation Engine*# \n '
                                                                           'Trouble: LATENCY\n '
                                                                           'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                                                              'createdDate': '2019-09-10 10:34:00-04:00'}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details])
        ticket_exists = await service_affecting_monitor._ticket_existence(85940, 'VC05200026138', 'LATENCY')
        assert ticket_exists is False
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def ticket_existence_no_notes_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        template_renderer = Mock()
        config = testconfig
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        tickets = {'tickets': [{'ticketID': 3521039, 'serial': 'VC05200026138'}]}
        ticket_details = {'ticket_details': {"ticketDetails": [{"detailValue": 'VC05200026138'}],
                                             "ticketNotes": [{"noteValue": None}]}}
        event_bus.rpc_request = CoroutineMock(side_effect=[tickets, ticket_details])
        ticket_exists = await service_affecting_monitor._ticket_existence(85940, 'VC05200026138', 'LATENCY')
        assert ticket_exists is False
        assert event_bus.rpc_request.called

    def compose_ticket_dict_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()

        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        edges_to_report = {
            "request_id": "E4irhhgzqTxmSMFudJSF5Z",
            "edge_id": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 137,
                "edge_id": 1602
            },
            "edge_info": {
                "enterprise_name": "Titan America|85940|",
                "edges": {
                    "name": "TEST",
                    "edgeState": "OFFLINE",
                    "serialNumber": "VC05200028729",
                },
                "links": [
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE1",
                            "displayName": "Test1",
                            "state": "DISCONNECTED",
                        }
                    },
                    {
                        'bestLatencyMsRx': 14,
                        'bestLatencyMsTx': 20,
                        "link": {
                            "interface": "GE2",
                            "displayName": "Test2",
                            "state": "DISCONNECTED",
                        }
                    }
                ]
            }
        }

        ticket_dict = service_affecting_monitor._compose_ticket_dict(edges_to_report,
                                                                     edges_to_report['edge_info']['links'][0],
                                                                     edges_to_report['edge_info']['links']
                                                                     [0]['bestLatencyMsRx'],
                                                                     edges_to_report['edge_info']['links']
                                                                     [0]['bestLatencyMsTx'],
                                                                     'LATENCY', 120)

        assert isinstance(ticket_dict, OrderedDict)

    def ticket_object_to_string_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}
        service_affecting_monitor = ServiceAffectingMonitor(event_bus, logger, scheduler, config, template_renderer)
        ticket_note = service_affecting_monitor._ticket_object_to_string(test_dict)
        assert ticket_note == '#*Automation Engine*# \nEdgeName: Test \nEdge Status: ok \n'
