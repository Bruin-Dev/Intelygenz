from datetime import datetime
from datetime import timedelta
from pytz import utc
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from dateutil.parser import parse
from shortuuid import uuid

from application import Outages
from application.actions import outage_monitoring as outage_monitoring_module
from application.actions.outage_monitoring import OutageMonitor
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(outage_monitoring_module, 'uuid', return_value=uuid_)


class TestServiceOutageMonitor:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        assert outage_monitor._event_bus is event_bus
        assert outage_monitor._logger is logger
        assert outage_monitor._scheduler is scheduler
        assert outage_monitor._config is config
        assert outage_monitor._outage_repository is outage_repository
        assert outage_monitor._bruin_repository is bruin_repository
        assert outage_monitor._velocloud_repository is velocloud_repository
        assert outage_monitor._notifications_repository is notifications_repository
        assert outage_monitor._triage_repository is triage_repository
        assert outage_monitor._customer_cache_repository is customer_cache_repository
        assert outage_monitor._metrics_repository is metrics_repository
        assert outage_monitor._digi_repository is digi_repository
        assert outage_monitor._ha_repository is ha_repository

        assert outage_monitor._autoresolve_serials_whitelist == set()

    @pytest.mark.asyncio
    async def start_service_outage_monitoring_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor.start_service_outage_monitoring(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_service_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_monitoring_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor.start_service_outage_monitoring(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=undefined,
            replace_existing=False,
            id='_service_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_outage_monitor_job_with_job_id_already_executing_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        try:
            await outage_monitor.start_service_outage_monitoring(exec_on_start=False)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                outage_monitor._outage_monitoring_process, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
                next_run_time=undefined,
                replace_existing=False,
                id='_service_outage_monitor_process',
            )

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_get_cache_request_having_202_status_test(self):
        get_cache_response = {
            'body': 'Cache is still being built for host(s): mettel_velocloud.net, metvco03.mettel.net',
            'status': 202,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=get_cache_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._process_velocloud_host = CoroutineMock()

        await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor._process_velocloud_host.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_get_cache_request_having_non_2xx_status_and_different_from_202_test(self):
        get_cache_response = {
            'body': 'No edges were found for the specified filters',
            'status': 404,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=get_cache_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._process_velocloud_host = CoroutineMock()

        await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor._process_velocloud_host.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_customer_cache_ready_and_edge_in_blacklist_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        get_cache_response = {
            'request_id': uuid(),
            'body': [
                {
                    'edge': edge_full_id,
                    'serial_number': 'VC1234567',
                    'last_contact': '2020-08-27T15:25:42.000',
                    'bruin_client_info': {
                        'client_id': 12345,
                        'client_name': 'Aperture Science',
                    }
                },
            ],
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=get_cache_response)

        velocloud_repository = Mock()
        velocloud_repository.get_edge_status = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['blacklisted_edges'] = [edge_full_id]

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        velocloud_repository.get_edge_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_ok_test(self):
        velocloud_host_1 = 'metvco03.mettel.net'
        velocloud_host_2 = 'metvco04.mettel.net'

        velocloud_host_1_customer_cache = [
            {
                'edge': {
                    "host": velocloud_host_1,
                    "enterprise_id": 1,
                    "edge_id": 1234
                },
                'serial_number': 'VC1234567',
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': 12345,
                    'client_name': 'Aperture Science',
                }
            }
        ]
        velocloud_host_2_customer_cache = [
            {
                'edge': {
                    "host": velocloud_host_2,
                    "enterprise_id": 2,
                    "edge_id": 1234
                },
                'serial_number': 'VC8901234',
                'last_contact': '2020-08-27T15:25:42.000',
                'bruin_client_info': {
                    'client_id': 12345,
                    'client_name': 'Aperture Science',
                }
            }
        ]
        customer_cache = velocloud_host_1_customer_cache + velocloud_host_2_customer_cache
        get_cache_response = {
            'body': customer_cache,
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=get_cache_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._process_velocloud_host = CoroutineMock()

        datetime_mock = Mock()
        current_time = datetime.now()
        datetime_mock.now = Mock(return_value=current_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor._process_velocloud_host.assert_has_awaits([
            call(velocloud_host_1, velocloud_host_1_customer_cache),
            call(velocloud_host_2, velocloud_host_2_customer_cache),
        ], any_order=True)

    @pytest.mark.asyncio
    async def process_velocloud_host_ok_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC8901234'
        edge_3_serial = 'VC5678901'

        edge_1_ha_serial = 'VC99999999'
        edge_2_ha_serial = 'VC88888888'
        edge_3_ha_serial = None

        edge_1_state = 'OFFLINE'
        edge_2_state = 'OFFLINE'
        edge_3_state = 'CONNECTED'

        edge_1_ha_state = 'FAILED'
        edge_2_ha_state = 'READY'
        edge_3_ha_state = None

        edge_1_ha_state_normalized = 'OFFLINE'
        edge_2_ha_state_normalized = 'CONNECTED'
        edge_3_ha_state_normalized = None

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 2
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        edge_3_enterprise_id = 3
        edge_3_id = 1
        edge_3_full_id = {'host': velocloud_host, 'enterprise_id': edge_3_enterprise_id, 'edge_id': edge_3_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_3 = {
            'edge': edge_3_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_3_serial,
            'ha_serial_number': edge_3_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_1_ha_partner = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_ha_serial,
            'ha_serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2_ha_partner = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_ha_serial,
            'ha_serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_2,
            cached_edge_3,
            cached_edge_1_ha_partner,
            cached_edge_2_ha_partner,
        ]

        links_with_edge_1_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        links_with_edge_2_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'GladOS',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'interface': 'Wheatley',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        links_with_edge_3_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_3_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_3_state,
            'edgeId': edge_3_id,
            'edgeSerialNumber': edge_3_serial,
            'edgeHASerialNumber': edge_3_ha_serial,
            'interface': 'Augmented',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_info = [
            links_with_edge_1_info,
            links_with_edge_2_info,
            links_with_edge_3_info,
        ]
        links_with_edge_info_response = {
            'body': links_with_edge_info,
            'status': 200,
        }

        edge_1_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_1_state,
            'enterpriseId': edge_1_enterprise_id,
            'haSerialNumber': edge_1_ha_serial,
            'haState': edge_1_ha_state,
            'id': edge_1_id,
            'name': 'Big Boss',
            'serialNumber': edge_1_serial,
        }
        edge_2_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_2_state,
            'enterpriseId': edge_2_enterprise_id,
            'haSerialNumber': edge_2_ha_serial,
            'haState': edge_2_ha_state,
            'id': edge_2_id,
            'name': 'GladOS',
            'serialNumber': edge_2_serial,
        }
        edge_3_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_3_state,
            'enterpriseId': edge_3_enterprise_id,
            'haSerialNumber': edge_3_ha_serial,
            'haState': edge_3_ha_state,
            'id': edge_3_id,
            'name': 'Adam Jensen',
            'serialNumber': edge_3_serial,
        }
        edges_network_enterprises = [
            edge_1_network_enterprises,
            edge_2_network_enterprises,
            edge_3_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        links_grouped_by_edge_1 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge_2 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'GladOS',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'links': [
                {
                    'interface': 'Wheatley',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge_3 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_3_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_3_state,
            'edgeId': edge_3_id,
            'edgeSerialNumber': edge_3_serial,
            'edgeHASerialNumber': edge_3_ha_serial,
            'links': [
                {
                    'interface': 'Augmented',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge = [
            links_grouped_by_edge_1,
            links_grouped_by_edge_2,
            links_grouped_by_edge_3,
        ]

        links_grouped_by_edge_1_with_ha_info = {
            **links_grouped_by_edge_1,
            'edgeHAState': edge_1_ha_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_edge_2_with_ha_info = {
            **links_grouped_by_edge_2,
            'edgeHAState': edge_2_ha_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_edge_3_with_ha_info = {
            **links_grouped_by_edge_3,
            'edgeHAState': edge_3_ha_state_normalized,
            'edgeIsHAPrimary': None,
        }
        links_grouped_by_edge_with_ha_info = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
            links_grouped_by_edge_3_with_ha_info,
        ]

        edge_1_ha_partner = {
            **links_grouped_by_edge_1_with_ha_info,
            'edgeSerialNumber': edge_1_ha_serial,
            'edgeState': edge_1_ha_state_normalized,
            'edgeHASerialNumber': edge_1_serial,
            'edgeHAState': edge_1_state,
            'edgeIsHAPrimary': False,
        }
        edge_2_ha_partner = {
            **links_grouped_by_edge_2_with_ha_info,
            'edgeSerialNumber': edge_2_ha_serial,
            'edgeState': edge_2_ha_state_normalized,
            'edgeHASerialNumber': edge_2_serial,
            'edgeHAState': edge_2_state,
            'edgeIsHAPrimary': False,
        }
        all_edges = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
            links_grouped_by_edge_3_with_ha_info,
            edge_1_ha_partner,
            edge_2_ha_partner,
        ]

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }
        edge_3_full_info = {
            'cached_info': cached_edge_3,
            'status': links_grouped_by_edge_3,
        }
        edge_1_ha_partner_full_info = {
            'cached_info': cached_edge_1_ha_partner,
            'status': edge_1_ha_partner,
        }
        edge_2_ha_partner_full_info = {
            'cached_info': cached_edge_2_ha_partner,
            'status': edge_2_ha_partner,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_2_full_info,
            edge_3_full_info,
            edge_1_ha_partner_full_info,
            edge_2_ha_partner_full_info,
        ]

        link_down_edges = [
            edge_3_full_info,
        ]
        hard_down_edges = []
        ha_link_down_edges = []
        ha_soft_down_edges = [
            edge_2_full_info,
        ]
        ha_hard_down_edges = [
            edge_1_full_info,
            edge_1_ha_partner_full_info,
        ]
        healthy_edges = [
            edge_2_ha_partner_full_info,
        ]

        relevant_ha_hard_down_edges = [
            edge_1_full_info,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(side_effect=[
            link_down_edges,
            hard_down_edges,
            ha_link_down_edges,
            ha_soft_down_edges,
            ha_hard_down_edges,
        ])
        outage_repository.should_document_outage = Mock(side_effect=[
            True,
            True,
            True,
            False,
        ])
        outage_repository.is_edge_up = Mock(side_effect=[
            False,
            False,
            False,
            False,
            True,
        ])

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_edge_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(return_value=all_edges)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        ha_repository.map_edges_with_ha_info.assert_called_once_with(
            links_grouped_by_edge, edges_network_enterprises
        )
        ha_repository.get_edges_with_standbys_as_standalone_edges.assert_called_once_with(
            links_grouped_by_edge_with_ha_info
        )
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, all_edges
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_has_calls([
            call(link_down_edges, Outages.LINK_DOWN),
            call(ha_soft_down_edges, Outages.HA_SOFT_DOWN),
            call(relevant_ha_hard_down_edges, Outages.HA_HARD_DOWN),
        ])
        for edge in healthy_edges:
            outage_monitor._run_ticket_autoresolve_for_edge.assert_awaited_once_with(edge)

    @pytest.mark.asyncio
    async def process_velocloud_host_with_links_request_returning_non_2xx_status_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_3_serial = 'VC5678901'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_3_enterprise_id = 3
        edge_3_id = 1
        edge_3_full_id = {'host': velocloud_host, 'enterprise_id': edge_3_enterprise_id, 'edge_id': edge_3_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_3 = {
            'edge': edge_3_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_3_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_3,
        ]

        links_with_edge_info_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        outage_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        outage_monitor._schedule_recheck_job_for_edges.assert_not_called()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_velocloud_host_with_network_enterprises_request_returning_non_2xx_status_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC8901234'
        edge_3_serial = 'VC5678901'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 2
        edge_2_id = 1

        edge_3_enterprise_id = 3
        edge_3_id = 1
        edge_3_full_id = {'host': velocloud_host, 'enterprise_id': edge_3_enterprise_id, 'edge_id': edge_3_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_3 = {
            'edge': edge_3_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_3_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_3,
        ]

        links_with_edge_1_info = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
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
        links_with_edge_2_info = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'Wheatley',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        links_with_edge_3_info = {
            'host': velocloud_host,
            'enterpriseName': 'Sarif Industries',
            'enterpriseId': edge_3_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Adam Jensen',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_3_id,
            'edgeSerialNumber': edge_3_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
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
        links_with_edge_info = [
            links_with_edge_1_info,
            links_with_edge_2_info,
            links_with_edge_3_info,
        ]
        links_with_edge_info_response = {
            'body': links_with_edge_info,
            'status': 200,
        }

        network_enterprises_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock()
        outage_repository.is_any_link_disconnected = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock()
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_not_called()
        outage_monitor._map_cached_edges_with_edges_status.assert_not_called()

        outage_monitor._schedule_recheck_job_for_edges.assert_not_called()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_velocloud_host_with_just_edges_in_healthy_state_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_ha_serial = 'VC99999999'
        edge_2_ha_serial = None

        edge_1_state = 'CONNECTED'
        edge_2_state = 'CONNECTED'

        edge_1_ha_state = 'READY'
        edge_2_ha_state = None

        edge_1_ha_state_normalized = 'CONNECTED'
        edge_2_ha_state_normalized = None

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_1_ha_partner = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_ha_serial,
            'ha_serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_2,
            cached_edge_1_ha_partner,
        ]

        links_with_edge_1_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        links_with_edge_2_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'interface': 'Augmented',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_info = [
            links_with_edge_1_info,
            links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': links_with_edge_info,
            'status': 200,
        }

        edge_1_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_1_state,
            'enterpriseId': edge_1_enterprise_id,
            'haSerialNumber': edge_1_ha_serial,
            'haState': edge_1_ha_state,
            'id': edge_1_id,
            'name': 'Big Boss',
            'serialNumber': edge_1_serial,
        }
        edge_2_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_2_state,
            'enterpriseId': edge_2_enterprise_id,
            'haSerialNumber': edge_2_ha_serial,
            'haState': edge_2_ha_state,
            'id': edge_2_id,
            'name': 'Adam Jensen',
            'serialNumber': edge_2_serial,
        }
        edges_network_enterprises = [
            edge_1_network_enterprises,
            edge_2_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        links_grouped_by_edge_1 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge_2 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'links': [
                {
                    'interface': 'Augmented',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge = [
            links_grouped_by_edge_1,
            links_grouped_by_edge_2,
        ]

        links_grouped_by_edge_1_with_ha_info = {
            **links_grouped_by_edge_1,
            'edgeHAState': edge_1_ha_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_edge_2_with_ha_info = {
            **links_grouped_by_edge_2,
            'edgeHAState': edge_2_ha_state_normalized,
            'edgeIsHAPrimary': None,
        }
        links_grouped_by_edge_with_ha_info = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
        ]

        edge_1_ha_partner = {
            **links_grouped_by_edge_1_with_ha_info,
            'edgeSerialNumber': edge_1_ha_serial,
            'edgeState': edge_1_ha_state_normalized,
            'edgeHASerialNumber': edge_1_serial,
            'edgeHAState': edge_1_state,
            'edgeIsHAPrimary': False,
        }
        all_edges = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
            edge_1_ha_partner,
        ]

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }
        edge_1_ha_partner_full_info = {
            'cached_info': cached_edge_1_ha_partner,
            'status': edge_1_ha_partner,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_2_full_info,
            edge_1_ha_partner_full_info,
        ]

        link_down_edges = []
        hard_down_edges = []
        ha_link_down_edges = []
        ha_soft_down_edges = []
        ha_hard_down_edges = []
        healthy_edges = [
            edge_1_full_info,
            edge_1_ha_partner_full_info,
            edge_2_full_info,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(side_effect=[
            link_down_edges, hard_down_edges, ha_link_down_edges, ha_soft_down_edges, ha_hard_down_edges,
        ])
        outage_repository.is_edge_up = Mock(return_value=True)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_edge_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(return_value=all_edges)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        ha_repository.map_edges_with_ha_info.assert_called_once_with(
            links_grouped_by_edge, edges_network_enterprises
        )
        ha_repository.get_edges_with_standbys_as_standalone_edges.assert_called_once_with(
            links_grouped_by_edge_with_ha_info
        )
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, all_edges
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_not_called()
        for edge in healthy_edges:
            outage_monitor._run_ticket_autoresolve_for_edge.assert_any_await(edge)

    @pytest.mark.asyncio
    async def process_velocloud_host_with_just_edges_in_link_down_state_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_ha_serial = None
        edge_2_ha_serial = None

        edge_1_state = 'CONNECTED'
        edge_2_state = 'CONNECTED'

        edge_1_ha_state = None
        edge_2_ha_state = None

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_2,
        ]

        links_with_edge_1_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'interface': 'REX',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_2_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'interface': 'Augmented',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_info = [
            links_with_edge_1_info,
            links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': links_with_edge_info,
            'status': 200,
        }

        edge_1_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_1_state,
            'enterpriseId': edge_1_enterprise_id,
            'haSerialNumber': edge_1_ha_serial,
            'haState': edge_1_ha_state,
            'id': edge_1_id,
            'name': 'Big Boss',
            'serialNumber': edge_1_serial,
        }
        edge_2_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_2_state,
            'enterpriseId': edge_2_enterprise_id,
            'haSerialNumber': edge_2_ha_serial,
            'haState': edge_2_ha_state,
            'id': edge_2_id,
            'name': 'Adam Jensen',
            'serialNumber': edge_2_serial,
        }
        edges_network_enterprises = [
            edge_1_network_enterprises,
            edge_2_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        links_grouped_by_edge_1 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge_2 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'links': [
                {
                    'interface': 'Augmented',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge = [
            links_grouped_by_edge_1,
            links_grouped_by_edge_2,
        ]

        links_grouped_by_edge_1_with_ha_info = {
            **links_grouped_by_edge_1,
            'edgeHAState': edge_1_ha_state,
            'edgeIsHAPrimary': None,
        }
        links_grouped_by_edge_2_with_ha_info = {
            **links_grouped_by_edge_2,
            'edgeHAState': edge_2_ha_state,
            'edgeIsHAPrimary': None,
        }
        links_grouped_by_edge_with_ha_info = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
        ]

        all_edges = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
        ]

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        link_down_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]
        hard_down_edges = []
        ha_link_down_edges = []
        ha_soft_down_edges = []
        ha_hard_down_edges = []

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(side_effect=[
            link_down_edges, hard_down_edges, ha_link_down_edges, ha_soft_down_edges, ha_hard_down_edges
        ])
        outage_repository.should_document_outage = Mock(return_value=True)
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_edge_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(return_value=all_edges)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        ha_repository.map_edges_with_ha_info.assert_called_once_with(
            links_grouped_by_edge, edges_network_enterprises
        )
        ha_repository.get_edges_with_standbys_as_standalone_edges.assert_called_once_with(
            links_grouped_by_edge_with_ha_info
        )
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, all_edges
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_called_once_with(link_down_edges, Outages.LINK_DOWN)
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_velocloud_host_with_just_edges_in_hard_down_state_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_ha_serial = None
        edge_2_ha_serial = None

        edge_1_state = 'OFFLINE'
        edge_2_state = 'OFFLINE'

        edge_1_ha_state = None
        edge_2_ha_state = None

        edge_1_ha_state_normalized = None
        edge_2_ha_state_normalized = None

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_2,
        ]

        links_with_edge_1_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'interface': 'REX',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_2_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'interface': 'Augmented',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_info = [
            links_with_edge_1_info,
            links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': links_with_edge_info,
            'status': 200,
        }

        edge_1_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_1_state,
            'enterpriseId': edge_1_enterprise_id,
            'haSerialNumber': edge_1_ha_serial,
            'haState': edge_1_ha_state,
            'id': edge_1_id,
            'name': 'Big Boss',
            'serialNumber': edge_1_serial,
        }
        edge_2_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_2_state,
            'enterpriseId': edge_2_enterprise_id,
            'haSerialNumber': edge_2_ha_serial,
            'haState': edge_2_ha_state,
            'id': edge_2_id,
            'name': 'Adam Jensen',
            'serialNumber': edge_2_serial,
        }
        edges_network_enterprises = [
            edge_1_network_enterprises,
            edge_2_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        links_grouped_by_edge_1 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge_2 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'links': [
                {
                    'interface': 'Augmented',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge = [
            links_grouped_by_edge_1,
            links_grouped_by_edge_2,
        ]

        links_grouped_by_edge_1_with_ha_info = {
            **links_grouped_by_edge_1,
            'edgeHAState': edge_1_ha_state_normalized,
            'edgeIsHAPrimary': None,
        }
        links_grouped_by_edge_2_with_ha_info = {
            **links_grouped_by_edge_2,
            'edgeHAState': edge_2_ha_state_normalized,
            'edgeIsHAPrimary': None,
        }
        links_grouped_by_edge_with_ha_info = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
        ]

        all_edges = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
        ]

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        link_down_edges = []
        hard_down_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]
        ha_soft_down_edges = []
        ha_link_down_edges = []
        ha_hard_down_edges = []

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(side_effect=[
            link_down_edges, hard_down_edges, ha_link_down_edges, ha_soft_down_edges, ha_hard_down_edges
        ])
        outage_repository.should_document_outage = Mock(return_value=True)
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_edge_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(return_value=all_edges)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        ha_repository.map_edges_with_ha_info.assert_called_once_with(
            links_grouped_by_edge, edges_network_enterprises
        )
        ha_repository.get_edges_with_standbys_as_standalone_edges.assert_called_once_with(
            links_grouped_by_edge_with_ha_info
        )
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, all_edges
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_called_once_with(hard_down_edges, Outages.HARD_DOWN)
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_velocloud_host_with_just_edges_in_HA_link_down_state_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_ha_serial = 'VC99999999'
        edge_2_ha_serial = 'VC88888888'

        edge_1_state = 'CONNECTED'
        edge_2_state = 'CONNECTED'

        edge_1_ha_state = 'READY'
        edge_2_ha_state = 'READY'

        edge_1_ha_state_normalized = 'CONNECTED'
        edge_2_ha_state_normalized = 'CONNECTED'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_1_ha_partner = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_ha_serial,
            'ha_serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2_ha_partner = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-27T02:23:59',
            'serial_number': edge_2_ha_serial,
            'ha_serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_2,
            cached_edge_1_ha_partner,
            cached_edge_2_ha_partner,
        ]

        links_with_edge_1_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'interface': 'REX',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_2_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'interface': 'Augmented',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_info = [
            links_with_edge_1_info,
            links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': links_with_edge_info,
            'status': 200,
        }

        edge_1_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_1_state,
            'enterpriseId': edge_1_enterprise_id,
            'haSerialNumber': edge_1_ha_serial,
            'haState': edge_1_ha_state,
            'id': edge_1_id,
            'name': 'Big Boss',
            'serialNumber': edge_1_serial,
        }
        edge_2_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_2_state,
            'enterpriseId': edge_2_enterprise_id,
            'haSerialNumber': edge_2_ha_serial,
            'haState': edge_2_ha_state,
            'id': edge_2_id,
            'name': 'Adam Jensen',
            'serialNumber': edge_2_serial,
        }
        edges_network_enterprises = [
            edge_1_network_enterprises,
            edge_2_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        links_grouped_by_edge_1 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge_2 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'links': [
                {
                    'interface': 'Augmented',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge = [
            links_grouped_by_edge_1,
            links_grouped_by_edge_2,
        ]

        links_grouped_by_edge_1_with_ha_info = {
            **links_grouped_by_edge_1,
            'edgeHAState': edge_1_ha_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_edge_2_with_ha_info = {
            **links_grouped_by_edge_2,
            'edgeHAState': edge_2_ha_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_edge_with_ha_info = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
        ]

        edge_1_ha_partner = {
            **links_grouped_by_edge_1_with_ha_info,
            'edgeSerialNumber': edge_1_ha_serial,
            'edgeState': edge_1_ha_state_normalized,
            'edgeHASerialNumber': edge_1_serial,
            'edgeHAState': edge_1_state,
            'edgeIsHAPrimary': False,
        }
        edge_2_ha_partner = {
            **links_grouped_by_edge_2_with_ha_info,
            'edgeSerialNumber': edge_2_ha_serial,
            'edgeState': edge_2_ha_state_normalized,
            'edgeHASerialNumber': edge_2_serial,
            'edgeHAState': edge_2_state,
            'edgeIsHAPrimary': False,
        }
        all_edges = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
            edge_1_ha_partner,
            edge_2_ha_partner,
        ]

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }
        edge_1_ha_partner_full_info = {
            'cached_info': cached_edge_1_ha_partner,
            'status': edge_1_ha_partner,
        }
        edge_2_ha_partner_full_info = {
            'cached_info': cached_edge_2_ha_partner,
            'status': edge_2_ha_partner,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_2_full_info,
            edge_1_ha_partner_full_info,
            edge_2_ha_partner_full_info,
        ]

        link_down_edges = []
        hard_down_edges = []
        ha_link_down_edges = [
            edge_1_full_info,
            edge_2_full_info,
            edge_1_ha_partner_full_info,
            edge_2_ha_partner_full_info,
        ]
        ha_soft_down_edges = []
        ha_hard_down_edges = []

        relevant_ha_link_down_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(side_effect=[
            link_down_edges, hard_down_edges, ha_link_down_edges, ha_soft_down_edges, ha_hard_down_edges
        ])
        outage_repository.should_document_outage = Mock(side_effect=[
            True,
            True,
            False,
            False,
        ])
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_edge_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(return_value=all_edges)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        ha_repository.map_edges_with_ha_info.assert_called_once_with(
            links_grouped_by_edge, edges_network_enterprises
        )
        ha_repository.get_edges_with_standbys_as_standalone_edges.assert_called_once_with(
            links_grouped_by_edge_with_ha_info
        )
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, all_edges
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_called_once_with(
            relevant_ha_link_down_edges, Outages.HA_LINK_DOWN
        )
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_velocloud_host_with_just_edges_in_HA_soft_down_state_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_serial = 'VC1234567'
        edge_ha_serial = 'VC99999999'
        edge_state = 'CONNECTED'
        edge_ha_state = 'FAILED'
        edge_ha_state_normalized = 'OFFLINE'

        edge_enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': edge_enterprise_id, 'edge_id': edge_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_serial,
            'ha_serial_number': edge_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_ha_partner = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_ha_serial,
            'ha_serial_number': edge_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge,
            cached_edge_ha_partner,
        ]

        links_with_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': edge_ha_serial,
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        links_with_edge_info = [
            links_with_edge_info,
        ]
        links_with_edge_info_response = {
            'body': links_with_edge_info,
            'status': 200,
        }

        edge_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_state,
            'enterpriseId': edge_enterprise_id,
            'haSerialNumber': edge_ha_serial,
            'haState': edge_ha_state,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_serial,
        }
        edges_network_enterprises = [
            edge_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        links_grouped_by_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': edge_ha_serial,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'STABLE',
                    'linkId': 5293,
                },
            ],
        }
        all_links_grouped_by_edge = [
            links_grouped_by_edge,
        ]

        links_grouped_by_edge_with_ha_info = {
            **links_grouped_by_edge,
            'edgeHAState': edge_ha_state_normalized,
            'edgeIsHAPrimary': True,
        }
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_edge_with_ha_info,
        ]

        edge_ha_partner = {
            **links_grouped_by_edge_with_ha_info,
            'edgeSerialNumber': edge_ha_serial,
            'edgeState': edge_ha_state_normalized,
            'edgeHASerialNumber': edge_serial,
            'edgeHAState': edge_state,
            'edgeIsHAPrimary': False,
        }
        all_edges = [
            links_grouped_by_edge_with_ha_info,
            edge_ha_partner,
        ]

        edge_full_info = {
            'cached_info': cached_edge,
            'status': links_grouped_by_edge,
        }
        edge_ha_partner_full_info = {
            'cached_info': cached_edge_ha_partner,
            'status': edge_ha_partner,
        }
        edges_full_info = [
            edge_full_info,
            edge_ha_partner_full_info,
        ]

        link_down_edges = []
        hard_down_edges = []
        ha_link_down_edges = []
        ha_soft_down_edges = [
            edge_ha_partner_full_info,
        ]
        ha_hard_down_edges = []
        healthy_edges = [
            edge_full_info,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=all_links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(side_effect=[
            link_down_edges, hard_down_edges, ha_link_down_edges, ha_soft_down_edges, ha_hard_down_edges
        ])
        outage_repository.is_edge_up = Mock(side_effect=[
            True,
            False,
        ])

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=all_links_grouped_by_edge_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(return_value=all_edges)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        ha_repository.map_edges_with_ha_info.assert_called_once_with(
            all_links_grouped_by_edge, edges_network_enterprises
        )
        ha_repository.get_edges_with_standbys_as_standalone_edges.assert_called_once_with(
            all_links_grouped_by_edge_with_ha_info
        )
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, all_edges
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_called_once_with(ha_soft_down_edges, Outages.HA_SOFT_DOWN)
        for edge in healthy_edges:
            outage_monitor._run_ticket_autoresolve_for_edge.assert_awaited_once_with(edge)

    @pytest.mark.asyncio
    async def process_velocloud_host_with_just_edges_in_HA_hard_down_state_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_ha_serial = 'VC99999999'
        edge_2_ha_serial = 'VC88888888'

        edge_1_state = 'OFFLINE'
        edge_2_state = 'OFFLINE'

        edge_1_ha_state = 'FAILED'
        edge_2_ha_state = 'FAILED'

        edge_1_ha_state_normalized = 'OFFLINE'
        edge_2_ha_state_normalized = 'OFFLINE'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'ha_serial_number': edge_1_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'ha_serial_number': edge_2_ha_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_1_ha_partner = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_ha_serial,
            'ha_serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2_ha_partner = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_ha_serial,
            'ha_serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_2,
            cached_edge_1_ha_partner,
            cached_edge_2_ha_partner,
        ]

        links_with_edge_1_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'interface': 'REX',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_2_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'interface': 'Augmented',
            'linkState': 'DISCONNECTED',
            'linkId': 5293,
        }
        links_with_edge_info = [
            links_with_edge_1_info,
            links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': links_with_edge_info,
            'status': 200,
        }

        edge_1_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_1_state,
            'enterpriseId': edge_1_enterprise_id,
            'haSerialNumber': edge_1_ha_serial,
            'haState': edge_1_ha_state,
            'id': edge_1_id,
            'name': 'Big Boss',
            'serialNumber': edge_1_serial,
        }
        edge_2_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_2_state,
            'enterpriseId': edge_2_enterprise_id,
            'haSerialNumber': edge_2_ha_serial,
            'haState': edge_2_ha_state,
            'id': edge_2_id,
            'name': 'Adam Jensen',
            'serialNumber': edge_2_serial,
        }
        edges_network_enterprises = [
            edge_1_network_enterprises,
            edge_2_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        links_grouped_by_edge_1 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_1_enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': edge_1_ha_serial,
            'links': [
                {
                    'interface': 'REX',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge_2 = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': edge_2_enterprise_id,
            'edgeName': 'Adam Jensen',
            'edgeState': edge_2_state,
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': edge_2_ha_serial,
            'links': [
                {
                    'interface': 'Augmented',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                },
            ],
        }
        links_grouped_by_edge = [
            links_grouped_by_edge_1,
            links_grouped_by_edge_2,
        ]

        links_grouped_by_edge_1_with_ha_info = {
            **links_grouped_by_edge_1,
            'edgeHAState': edge_1_ha_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_edge_2_with_ha_info = {
            **links_grouped_by_edge_2,
            'edgeHAState': edge_2_ha_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_edge_with_ha_info = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
        ]

        edge_1_ha_partner = {
            **links_grouped_by_edge_1_with_ha_info,
            'edgeSerialNumber': edge_1_ha_serial,
            'edgeState': edge_1_ha_state_normalized,
            'edgeHASerialNumber': edge_1_serial,
            'edgeHAState': edge_1_state,
            'edgeIsHAPrimary': False,
        }
        edge_2_ha_partner = {
            **links_grouped_by_edge_2_with_ha_info,
            'edgeSerialNumber': edge_2_ha_serial,
            'edgeState': edge_2_ha_state_normalized,
            'edgeHASerialNumber': edge_2_serial,
            'edgeHAState': edge_2_state,
            'edgeIsHAPrimary': False,
        }
        all_edges = [
            links_grouped_by_edge_1_with_ha_info,
            links_grouped_by_edge_2_with_ha_info,
            edge_1_ha_partner,
            edge_2_ha_partner,
        ]

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }
        edge_1_ha_partner_full_info = {
            'cached_info': cached_edge_1_ha_partner,
            'status': edge_1_ha_partner,
        }
        edge_2_ha_partner_full_info = {
            'cached_info': cached_edge_2_ha_partner,
            'status': edge_2_ha_partner,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_2_full_info,
            edge_1_ha_partner_full_info,
            edge_2_ha_partner_full_info,
        ]

        link_down_edges = []
        hard_down_edges = []
        ha_link_down_edges = []
        ha_soft_down_edges = []
        ha_hard_down_edges = [
            edge_1_full_info,
            edge_2_full_info,
            edge_1_ha_partner_full_info,
            edge_2_ha_partner_full_info,
        ]

        relevant_ha_hard_down_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(side_effect=[
            link_down_edges, hard_down_edges, ha_link_down_edges, ha_soft_down_edges, ha_hard_down_edges
        ])
        outage_repository.should_document_outage = Mock(side_effect=[
            True,
            True,
            False,
            False,
        ])
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_edge_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(return_value=all_edges)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        ha_repository.map_edges_with_ha_info.assert_called_once_with(
            links_grouped_by_edge, edges_network_enterprises
        )
        ha_repository.get_edges_with_standbys_as_standalone_edges.assert_called_once_with(
            links_grouped_by_edge_with_ha_info
        )
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, all_edges
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_called_once_with(
            relevant_ha_hard_down_edges, Outages.HA_HARD_DOWN
        )
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    def map_cached_edges_with_edges_status_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC8901234'
        edge_3_serial = 'VC5678901'
        edge_4_serial = 'VC2345678'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 2
        edge_2_id = 1

        edge_3_enterprise_id = 3
        edge_3_id = 1
        edge_3_full_id = {'host': velocloud_host, 'enterprise_id': edge_3_enterprise_id, 'edge_id': edge_3_id}

        edge_4_enterprise_id = 4
        edge_4_id = 1
        edge_4_full_id = {'host': velocloud_host, 'enterprise_id': edge_4_enterprise_id, 'edge_id': edge_4_id}

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_3 = {
            'edge': edge_3_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_3_serial,
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_4 = {
            'edge': edge_4_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_4_serial,
            'bruin_client_info': bruin_client_info,
        }
        customer_cache_for_velocloud_host = [
            cached_edge_1,
            cached_edge_3,
            cached_edge_4,
        ]

        links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
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
            ],
        }
        links_grouped_by_edge_2 = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_2_id,
            'edgeSerialNumber': edge_2_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'Wheatley',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'STABLE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        links_grouped_by_edge_3 = {
            'host': velocloud_host,
            'enterpriseName': 'Sarif Industries',
            'enterpriseId': edge_3_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Adam Jensen',
            'edgeState': 'OFFLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_3_id,
            'edgeSerialNumber': edge_3_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'Augmented',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        links_grouped_by_edge = [
            links_grouped_by_edge_1,
            links_grouped_by_edge_2,
            links_grouped_by_edge_3,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        outage_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        result = outage_monitor._map_cached_edges_with_edges_status(
            customer_cache_for_velocloud_host, links_grouped_by_edge
        )

        expected = [
            {
                'cached_info': cached_edge_1,
                'status': links_grouped_by_edge_1,
            },
            {
                'cached_info': cached_edge_3,
                'status': links_grouped_by_edge_3,
            },
        ]
        assert result == expected

    def schedule_recheck_job_for_edges_test(self):
        outage_type = Outages.HARD_DOWN  # We can use whatever outage type
        edges = [
            {
                'cached_info': {
                    'edge': {
                        'host': 'mettel.velocloud.net',
                        'enterprise_id': 1,
                        'edge_id': 1
                    },
                    'last_contact': '2020-08-17T02:23:59',
                    'serial_number': 'VC1234567',
                    'bruin_client_info': {
                        'client_id': 9994,
                        'client_name': 'METTEL/NEW YORK',
                    },
                },
                'status': [
                    {
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
                        'links': [
                            {
                                'displayName': '70.59.5.185',
                                'isp': None,
                                'interface': 'REX',
                                'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                                'linkState': 'DISCONNECTED',
                                'linkLastActive': '2020-09-29T04:45:15.000Z',
                                'linkVpnState': 'STABLE',
                                'linkId': 5293,
                                'linkIpAddress': '70.59.5.185',
                            },
                        ],
                    }
                ]
            }
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        outage_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                outage_monitor._schedule_recheck_job_for_edges(edges, outage_type)

        expected_run_date = next_run_time + timedelta(seconds=config.MONITOR_CONFIG['quarantine'][outage_type])
        scheduler.add_job.assert_called_once_with(
            outage_monitor._recheck_edges_for_ticket_creation, 'date',
            args=[edges, outage_type],
            run_date=expected_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f'{outage_type.value}_ticket_creation_recheck',
        )

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_non_whitelisted_edge_test(self):
        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1
                },
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': 'VC1234567',
                'bruin_client_info': {
                    'client_id': 9994,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = set()

        await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_retrieval_of_ticket_returning_non_2xx_status_test(self):
        serial_number = 'VC1234567'
        client_id = 9994

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge = {
            'cached_info': {
                'edge': edge_full_id,
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_response = {
            'body': "Invalid parameters",
            'status': 400,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_down_edge_events = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}

        await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        bruin_repository.get_ticket_details.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_no_open_outage_ticket_found_test(self):
        serial_number = 'VC1234567'
        client_id = 9994

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge = {
            'cached_info': {
                'edge': edge_full_id,
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_response = {
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}

        await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        bruin_repository.get_ticket_details.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_ticket_not_created_by_automation_engine_test(self):
        serial_number = 'VC1234567'
        client_id = 9994

        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge = {
            'cached_info': {
                'edge': edge_full_id,
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_1_id = 99999
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": testconfig.PRODUCT_CATEGORY,
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "InterMapper Service",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=False)

        await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_retrieval_of_ticket_details_returning_non_2xx_status_test(self):
        serial_number = 'VC1234567'
        client_id = 9994

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1
                },
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_1_id = 99999
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": testconfig.PRODUCT_CATEGORY,
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        ticket_details_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock()

        await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_last_outage_spotted_long_time_ago_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        client_id = 9994

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1
                },
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number_1,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number_1,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": testconfig.PRODUCT_CATEGORY,
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }
        outage_ticket_detail_2 = {
            "detailID": 2746938,
            "detailValue": serial_number_2,
            "detailStatus": "I",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_5,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}

        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=False)

        await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_resolve_limit_exceeded_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        client_id = 9994

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1
                },
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number_1,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number_1,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": testconfig.PRODUCT_CATEGORY,
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_5,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        outage_repository = Mock()
        outage_repository.is_outage_ticket_detail_auto_resolvable = Mock(return_value=False)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor._is_detail_resolved = Mock()

        await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, serial_number_1, max_autoresolves=config.MONITOR_CONFIG['max_autoresolves']
        )
        outage_monitor._is_detail_resolved.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_ticket_already_resolved_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        client_id = 12345

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1
                },
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number_1,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number_1,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": testconfig.PRODUCT_CATEGORY,
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "R",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_4,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor._is_detail_resolved = Mock(return_value=True)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, serial_number_1, max_autoresolves=config.MONITOR_CONFIG['max_autoresolves']
        )
        outage_monitor._is_detail_resolved.assert_called_once_with(outage_ticket_detail_1)
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        outage_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_environment_different_from_production_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        client_id = 12345

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1
                },
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number_1,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number_1,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": testconfig.PRODUCT_CATEGORY,
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "R",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_5,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        config = testconfig

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor._is_detail_resolved = Mock(return_value=True)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'dev'):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, serial_number_1, max_autoresolves=config.MONITOR_CONFIG['max_autoresolves']
        )
        outage_monitor._is_detail_resolved.assert_called_once_with(outage_ticket_detail_1)
        bruin_repository.resolve_ticket.assert_not_awaited()
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        outage_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_resolve_outage_return_non_2xx_status_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        client_id = 12345

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1
                },
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number_1,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number_1,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": testconfig.PRODUCT_CATEGORY,
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1_id = 2746937
        outage_ticket_detail_1 = {
            "detailID": outage_ticket_detail_1_id,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_5,
        ]

        resolve_outage_ticket_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        config = testconfig

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor._is_detail_resolved = Mock(return_value=False)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, serial_number_1, max_autoresolves=config.MONITOR_CONFIG['max_autoresolves']
        )
        outage_monitor._is_detail_resolved.assert_called_once_with(outage_ticket_detail_1)
        bruin_repository.resolve_ticket.assert_awaited_once_with(outage_ticket_1_id, outage_ticket_detail_1_id)
        bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            outage_ticket_1_id, service_number=serial_number_1, detail_id=outage_ticket_detail_1_id
        )
        bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()
        outage_monitor._notify_successful_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_all_conditions_met_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        client_id = 12345

        edge = {
            'cached_info': {
                'edge': {
                    'host': 'mettel.velocloud.net',
                    'enterprise_id': 1,
                    'edge_id': 1
                },
                'last_contact': '2020-08-17T02:23:59',
                'serial_number': serial_number_1,
                'bruin_client_info': {
                    'client_id': client_id,
                    'client_name': 'METTEL/NEW YORK',
                },
            },
            'status': [
                {
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
                    'edgeSerialNumber': serial_number_1,
                    'edgeHASerialNumber': None,
                    'edgeModelNumber': 'edge520',
                    'edgeLatitude': None,
                    'edgeLongitude': None,
                    'links': [
                        {
                            'displayName': '70.59.5.185',
                            'isp': None,
                            'interface': 'REX',
                            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                            'linkState': 'DISCONNECTED',
                            'linkLastActive': '2020-09-29T04:45:15.000Z',
                            'linkVpnState': 'STABLE',
                            'linkId': 5293,
                            'linkIpAddress': '70.59.5.185',
                        },
                    ],
                }
            ]
        }

        outage_ticket_1_id = 99999
        outage_ticket_1_creation_date = "9/25/2020 6:31:54 AM"
        outage_ticket_1 = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": outage_ticket_1_id,
            "category": testconfig.PRODUCT_CATEGORY,
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": outage_ticket_1_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            'body': [
                outage_ticket_1
            ],
            'status': 200,
        }

        outage_ticket_detail_1_id = 2746937
        outage_ticket_detail_1 = {
            "detailID": outage_ticket_detail_1_id,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }
        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        relevant_notes_for_edge = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_5,
        ]

        resolve_outage_ticket_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        config = testconfig

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor._is_detail_resolved = Mock(return_value=False)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, serial_number_1, max_autoresolves=config.MONITOR_CONFIG['max_autoresolves']
        )
        outage_monitor._is_detail_resolved.assert_called_once_with(outage_ticket_detail_1)
        bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            outage_ticket_1_id, service_number=serial_number_1, detail_id=outage_ticket_detail_1_id
        )
        bruin_repository.resolve_ticket.assert_awaited_once_with(outage_ticket_1_id, outage_ticket_detail_1_id)
        bruin_repository.append_autoresolve_note_to_ticket.assert_awaited_once_with(outage_ticket_1_id, serial_number_1)
        outage_monitor._notify_successful_autoresolve.assert_awaited_once_with(outage_ticket_1_id)

    def was_ticket_created_by_automation_engine_test(self):
        ticket = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": 12345,
            "category": "SD-WAN",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "Intelygenz Ai",
        }
        result = OutageMonitor._was_ticket_created_by_automation_engine(ticket)
        assert result is True

        ticket = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": 12345,
            "category": "SD-WAN",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "InterMapper Service",
        }
        result = OutageMonitor._was_ticket_created_by_automation_engine(ticket)
        assert result is False

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_not_found_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        ticket_notes = []

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(minutes=59, seconds=59)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, seconds=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_found_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'
        reopen_timestamp = '2021-01-02T11:00:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": triage_timestamp,
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
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_having_old_watermark_found_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'
        reopen_timestamp = '2021-01-02T11:00:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": triage_timestamp,
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*Automation Engine*#\nRe-opening\nTimeStamp: 2021-01-03 10:18:16-05:00",
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
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_note_found_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": triage_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        datetime_mock = Mock()

        new_now = parse(triage_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_note_having_old_watermark_found_test(
            self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'
        triage_timestamp = '2021-01-02T10:18:16.71-05:00'

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*Automation Engine*#\nTriage (VeloCloud)\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                'VC1234567',
            ],
            "createdDate": triage_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        datetime_mock = Mock()

        new_now = parse(triage_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    @pytest.mark.asyncio
    async def notify_successful_autoresolve_test(self):
        ticket_id = 12345
        bruin_client_id = 67890

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        outage_repository = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor._notify_successful_autoresolve(ticket_id)

        autoresolve_slack_message = (
            f'Outage ticket {ticket_id} was autoresolved. Details at https://app.bruin.com/t/{ticket_id}'
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(autoresolve_slack_message)

    def get_first_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = OutageMonitor._get_first_element_matching(iterable=payload, condition=cond)
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

        result = OutageMonitor._get_first_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    @pytest.mark.asyncio
    async def recheck_edges_with_links_request_returning_non_2xx_status_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_state = 'OFFLINE'
        edge_standby_state = 'OFFLINE'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
        }
        edge_standby_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_standby_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_standby_serial,
            'edgeHASerialNumber': edge_primary_serial,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }
        edge_with_links_standby = {
            **edge_standby_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_with_links_and_ha_info_primary = {
            **edge_with_links_primary,
            'edgeHAState': edge_standby_state,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_and_ha_info_standby = {
            **edge_with_links_standby,
            'edgeHAState': edge_primary_state,
            'edgeIsHAPrimary': False,
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_and_ha_info_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        links_with_edge_info_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        outage_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_not_awaited()
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_networks_enterprises_request_returning_non_2xx_status_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_state = 'OFFLINE'
        edge_standby_state = 'OFFLINE'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
        }
        edge_standby_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_standby_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_standby_serial,
            'edgeHASerialNumber': edge_primary_serial,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }
        edge_with_links_standby = {
            **edge_standby_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_with_links_and_ha_info_primary = {
            **edge_with_links_primary,
            'edgeHAState': edge_standby_state,
            'edgeIsHAPrimary': True,
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_and_ha_info_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        link_1_with_edge_info = {
            **edge_primary_info,
            **edge_link_1_info,
        }
        links_with_edge_info_response = {
            'body': [
                link_1_with_edge_info,
            ],
            'status': 200,
        }

        network_enterprises_response = {
            'body': 'Got internal error from Velocloud',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        outage_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.get_network_enterprises.assert_awaited_once_with(velocloud_host=velocloud_host)
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_just_edges_in_healthy_state_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_initial_state = 'OFFLINE'
        edge_standby_initial_state_normalized = 'OFFLINE'

        edge_primary_new_state = 'CONNECTED'
        edge_standby_new_state_raw = 'READY'
        edge_standby_new_state_normalized = 'CONNECTED'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }
        cached_edge_standby = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_standby_serial,
            'ha_serial_number': edge_primary_serial,
            'bruin_client_info': bruin_client_info,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_initial_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'edgeHAState': edge_standby_initial_state_normalized,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_primary_new_state,
            'enterpriseId': enterprise_id,
            'haSerialNumber': edge_standby_serial,
            'haState': edge_standby_new_state_raw,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_primary_serial,
        }
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        new_links_with_primary_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            **edge_link_1_info,
        }
        new_links_with_edge_info = [
            new_links_with_primary_edge_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

        new_links_grouped_by_primary_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                edge_link_1_info
            ],
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_primary_edge,
        ]

        links_grouped_by_primary_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeHAState': edge_standby_new_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_standby_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeSerialNumber': edge_standby_serial,
            'edgeState': edge_standby_new_state_normalized,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeHAState': edge_primary_new_state,
            'edgeIsHAPrimary': False,
        }
        links_grouped_by_primary_edges_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
        ]
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
            links_grouped_by_standby_edge_with_ha_info,
        ]

        new_primary_edge_full_info = {
            'cached_info': cached_edge_primary,
            'status': links_grouped_by_primary_edge_with_ha_info,
        }
        new_standby_edge_full_info = {
            'cached_info': cached_edge_standby,
            'status': links_grouped_by_standby_edge_with_ha_info,
        }
        new_edges_full_info = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        edges_in_same_outage_state = []
        edges_in_healthy_state = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(return_value=edges_in_same_outage_state)
        outage_repository.is_edge_up = Mock(return_value=True)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_primary_edges_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(
            return_value=all_links_grouped_by_edge_with_ha_info
        )

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        for edge in edges_in_healthy_state:
            outage_monitor._run_ticket_autoresolve_for_edge.assert_any_await(edge)

    @pytest.mark.asyncio
    async def recheck_edges_with_edge_state_switching_to_a_different_outage_type_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_initial_state = 'OFFLINE'
        edge_standby_initial_state_normalized = 'OFFLINE'

        # Edge transitioned from HA_HARD_DOWN to HA_SOFT_DOWN
        edge_primary_new_state = 'OFFLINE'
        edge_standby_new_state_raw = 'READY'
        edge_standby_new_state_normalized = 'CONNECTED'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }
        cached_edge_standby = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_standby_serial,
            'ha_serial_number': edge_primary_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_initial_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'edgeHAState': edge_standby_initial_state_normalized,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_primary_new_state,
            'enterpriseId': enterprise_id,
            'haSerialNumber': edge_standby_serial,
            'haState': edge_standby_new_state_raw,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_primary_serial,
        }
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        new_links_with_primary_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            **edge_link_1_info,
        }
        new_links_with_edge_info = [
            new_links_with_primary_edge_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

        new_links_grouped_by_primary_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                edge_link_1_info
            ],
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_primary_edge,
        ]

        links_grouped_by_primary_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeHAState': edge_standby_new_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_standby_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeSerialNumber': edge_standby_serial,
            'edgeState': edge_standby_new_state_normalized,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeHAState': edge_primary_new_state,
            'edgeIsHAPrimary': False,
        }
        links_grouped_by_primary_edges_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
        ]
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
            links_grouped_by_standby_edge_with_ha_info,
        ]

        new_primary_edge_full_info = {
            'cached_info': cached_edge_primary,
            'status': links_grouped_by_primary_edge_with_ha_info,
        }
        new_standby_edge_full_info = {
            'cached_info': cached_edge_standby,
            'status': links_grouped_by_standby_edge_with_ha_info,
        }
        new_edges_full_info = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        edges_in_same_outage_state = []

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(return_value=edges_in_same_outage_state)
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_primary_edges_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(
            return_value=all_links_grouped_by_edge_with_ha_info
        )

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_edges_still_in_same_outage_state_and_no_production_env_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_initial_state = 'OFFLINE'
        edge_standby_initial_state_normalized = 'OFFLINE'

        edge_primary_new_state = 'OFFLINE'
        edge_standby_new_state_raw = 'FAILED'
        edge_standby_new_state_normalized = 'OFFLINE'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        bruin_client_info = {
            'client_id': 9994,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }
        cached_edge_standby = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_standby_serial,
            'ha_serial_number': edge_primary_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_initial_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'edgeHAState': edge_standby_initial_state_normalized,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_primary_new_state,
            'enterpriseId': enterprise_id,
            'haSerialNumber': edge_standby_serial,
            'haState': edge_standby_new_state_raw,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_primary_serial,
        }
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        new_links_with_primary_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            **edge_link_1_info,
        }
        new_links_with_edge_info = [
            new_links_with_primary_edge_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

        new_links_grouped_by_primary_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                edge_link_1_info
            ],
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_primary_edge,
        ]

        links_grouped_by_primary_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeHAState': edge_standby_new_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_standby_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeSerialNumber': edge_standby_serial,
            'edgeState': edge_standby_new_state_normalized,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeHAState': edge_primary_new_state,
            'edgeIsHAPrimary': False,
        }
        links_grouped_by_primary_edges_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
        ]
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
            links_grouped_by_standby_edge_with_ha_info,
        ]

        new_primary_edge_full_info = {
            'cached_info': cached_edge_primary,
            'status': links_grouped_by_primary_edge_with_ha_info,
        }
        new_standby_edge_full_info = {
            'cached_info': cached_edge_standby,
            'status': links_grouped_by_standby_edge_with_ha_info,
        }
        new_edges_full_info = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        edges_in_same_outage_state = [
            new_primary_edge_full_info
        ]

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(return_value=edges_in_same_outage_state)
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_primary_edges_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(
            return_value=all_links_grouped_by_edge_with_ha_info
        )

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'dev'):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_edges_still_in_same_outage_state_and_ticket_creation_returning_200_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_initial_state = 'OFFLINE'
        edge_standby_initial_state_normalized = 'OFFLINE'

        edge_primary_new_state = 'OFFLINE'
        edge_standby_new_state_raw = 'FAILED'
        edge_standby_new_state_normalized = 'OFFLINE'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }
        cached_edge_standby = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_standby_serial,
            'ha_serial_number': edge_primary_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_initial_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'edgeHAState': edge_standby_initial_state_normalized,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_primary_new_state,
            'enterpriseId': enterprise_id,
            'haSerialNumber': edge_standby_serial,
            'haState': edge_standby_new_state_raw,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_primary_serial,
        }
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        new_links_with_primary_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            **edge_link_1_info,
        }
        new_links_with_edge_info = [
            new_links_with_primary_edge_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

        new_links_grouped_by_primary_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                edge_link_1_info
            ],
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_primary_edge,
        ]

        links_grouped_by_primary_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeHAState': edge_standby_new_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_standby_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeSerialNumber': edge_standby_serial,
            'edgeState': edge_standby_new_state_normalized,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeHAState': edge_primary_new_state,
            'edgeIsHAPrimary': False,
        }
        links_grouped_by_primary_edges_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
        ]
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
            links_grouped_by_standby_edge_with_ha_info,
        ]

        new_primary_edge_full_info = {
            'cached_info': cached_edge_primary,
            'status': links_grouped_by_primary_edge_with_ha_info,
        }
        new_standby_edge_full_info = {
            'cached_info': cached_edge_standby,
            'status': links_grouped_by_standby_edge_with_ha_info,
        }
        new_edges_full_info = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        edges_in_same_outage_state = [
            new_primary_edge_full_info
        ]

        ticket_id = 12345
        ticket_creation_response = {
            'request_id': uuid_,
            'body': ticket_id,
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=ticket_creation_response)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(return_value=edges_in_same_outage_state)
        outage_repository.is_edge_up = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_primary_edges_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(
            return_value=all_links_grouped_by_edge_with_ha_info
        )

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._append_triage_note = CoroutineMock()
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._check_for_digi_reboot = CoroutineMock()
        outage_monitor._change_ticket_severity = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, edge_primary_serial)
        outage_monitor._append_triage_note.assert_awaited_once_with(
            ticket_id, cached_edge_primary, links_grouped_by_primary_edge_with_ha_info, outage_type,
        )
        outage_monitor._change_ticket_severity.assert_awaited_once_with(
            ticket_id=ticket_id,
            edge_status=links_grouped_by_primary_edge_with_ha_info,
            check_ticket_tasks=False,
        )
        outage_monitor._check_for_digi_reboot.assert_awaited_once_with(
            ticket_id, logical_id_list, edge_primary_serial, links_grouped_by_primary_edge_with_ha_info,
        )
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_edges_still_in_same_outage_state_and_ticket_creation_returning_409_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_initial_state = 'OFFLINE'
        edge_standby_initial_state_normalized = 'OFFLINE'

        edge_primary_new_state = 'OFFLINE'
        edge_standby_new_state_raw = 'FAILED'
        edge_standby_new_state_normalized = 'OFFLINE'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }
        cached_edge_standby = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_standby_serial,
            'ha_serial_number': edge_primary_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_initial_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'edgeHAState': edge_standby_initial_state_normalized,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_primary_new_state,
            'enterpriseId': enterprise_id,
            'haSerialNumber': edge_standby_serial,
            'haState': edge_standby_new_state_raw,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_primary_serial,
        }
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        new_links_with_primary_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            **edge_link_1_info,
        }
        new_links_with_edge_info = [
            new_links_with_primary_edge_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

        new_links_grouped_by_primary_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                edge_link_1_info
            ],
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_primary_edge,
        ]

        links_grouped_by_primary_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeHAState': edge_standby_new_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_standby_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeSerialNumber': edge_standby_serial,
            'edgeState': edge_standby_new_state_normalized,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeHAState': edge_primary_new_state,
            'edgeIsHAPrimary': False,
        }
        links_grouped_by_primary_edges_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
        ]
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
            links_grouped_by_standby_edge_with_ha_info,
        ]

        new_primary_edge_full_info = {
            'cached_info': cached_edge_primary,
            'status': links_grouped_by_primary_edge_with_ha_info,
        }
        new_standby_edge_full_info = {
            'cached_info': cached_edge_standby,
            'status': links_grouped_by_standby_edge_with_ha_info,
        }
        new_edges_full_info = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        edges_in_same_outage_state = [
            new_primary_edge_full_info
        ]

        ticket_id = 12345
        ticket_creation_response = {
            'request_id': uuid_,
            'body': ticket_id,
            'status': 409,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=ticket_creation_response)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(return_value=edges_in_same_outage_state)
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_primary_edges_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(
            return_value=all_links_grouped_by_edge_with_ha_info
        )

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._check_for_failed_digi_reboot = CoroutineMock()
        outage_monitor._change_ticket_severity = CoroutineMock()
        outage_monitor._attempt_forward_to_asr = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, edge_primary_serial)
        outage_monitor._change_ticket_severity.assert_awaited_once_with(
            ticket_id=ticket_id,
            edge_status=links_grouped_by_primary_edge_with_ha_info,
            check_ticket_tasks=True,
        )
        outage_monitor._check_for_failed_digi_reboot.assert_awaited_once_with(
            ticket_id, logical_id_list, edge_primary_serial, links_grouped_by_primary_edge_with_ha_info,
        )
        outage_monitor._attempt_forward_to_asr.assert_awaited_once_with(
            cached_edge_primary, links_grouped_by_primary_edge_with_ha_info, ticket_id,
        )
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_edges_still_in_same_outage_state_and_ticket_creation_returning_471_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_initial_state = 'OFFLINE'
        edge_standby_initial_state_normalized = 'OFFLINE'

        edge_primary_new_state = 'OFFLINE'
        edge_standby_new_state_raw = 'FAILED'
        edge_standby_new_state_normalized = 'OFFLINE'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }
        cached_edge_standby = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_standby_serial,
            'ha_serial_number': edge_primary_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_initial_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'edgeHAState': edge_standby_initial_state_normalized,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_primary_new_state,
            'enterpriseId': enterprise_id,
            'haSerialNumber': edge_standby_serial,
            'haState': edge_standby_new_state_raw,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_primary_serial,
        }
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        new_links_with_primary_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            **edge_link_1_info,
        }
        new_links_with_edge_info = [
            new_links_with_primary_edge_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

        new_links_grouped_by_primary_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                edge_link_1_info
            ],
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_primary_edge,
        ]

        links_grouped_by_primary_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeHAState': edge_standby_new_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_standby_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeSerialNumber': edge_standby_serial,
            'edgeState': edge_standby_new_state_normalized,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeHAState': edge_primary_new_state,
            'edgeIsHAPrimary': False,
        }
        links_grouped_by_primary_edges_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
        ]
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
            links_grouped_by_standby_edge_with_ha_info,
        ]

        new_primary_edge_full_info = {
            'cached_info': cached_edge_primary,
            'status': links_grouped_by_primary_edge_with_ha_info,
        }
        new_standby_edge_full_info = {
            'cached_info': cached_edge_standby,
            'status': links_grouped_by_standby_edge_with_ha_info,
        }
        new_edges_full_info = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        edges_in_same_outage_state = [
            new_primary_edge_full_info
        ]

        ticket_id = 12345
        ticket_creation_response = {
            'request_id': uuid_,
            'body': ticket_id,
            'status': 471,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=ticket_creation_response)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(return_value=edges_in_same_outage_state)
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_primary_edges_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(
            return_value=all_links_grouped_by_edge_with_ha_info
        )

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._check_for_digi_reboot = CoroutineMock()
        outage_monitor._change_ticket_severity = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, edge_primary_serial)
        outage_monitor._change_ticket_severity.assert_awaited_once_with(
            ticket_id=ticket_id,
            edge_status=links_grouped_by_primary_edge_with_ha_info,
            check_ticket_tasks=True,
        )
        outage_monitor._check_for_digi_reboot.assert_awaited_once_with(
            ticket_id, logical_id_list, edge_primary_serial, links_grouped_by_primary_edge_with_ha_info,
        )
        outage_monitor._reopen_outage_ticket.assert_awaited_once_with(
            ticket_id, links_grouped_by_primary_edge_with_ha_info, cached_edge_primary, outage_type
        )
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_edges_still_in_same_outage_state_and_ticket_creation_returning_472_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_initial_state = 'OFFLINE'
        edge_standby_initial_state_normalized = 'OFFLINE'

        edge_primary_new_state = 'OFFLINE'
        edge_standby_new_state_raw = 'FAILED'
        edge_standby_new_state_normalized = 'OFFLINE'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }
        cached_edge_standby = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_standby_serial,
            'ha_serial_number': edge_primary_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_initial_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'edgeHAState': edge_standby_initial_state_normalized,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_primary_new_state,
            'enterpriseId': enterprise_id,
            'haSerialNumber': edge_standby_serial,
            'haState': edge_standby_new_state_raw,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_primary_serial,
        }
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        new_links_with_primary_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            **edge_link_1_info,
        }
        new_links_with_edge_info = [
            new_links_with_primary_edge_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

        new_links_grouped_by_primary_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                edge_link_1_info
            ],
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_primary_edge,
        ]

        links_grouped_by_primary_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeHAState': edge_standby_new_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_standby_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeSerialNumber': edge_standby_serial,
            'edgeState': edge_standby_new_state_normalized,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeHAState': edge_primary_new_state,
            'edgeIsHAPrimary': False,
        }
        links_grouped_by_primary_edges_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
        ]
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
            links_grouped_by_standby_edge_with_ha_info,
        ]

        new_primary_edge_full_info = {
            'cached_info': cached_edge_primary,
            'status': links_grouped_by_primary_edge_with_ha_info,
        }
        new_standby_edge_full_info = {
            'cached_info': cached_edge_standby,
            'status': links_grouped_by_standby_edge_with_ha_info,
        }
        new_edges_full_info = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        edges_in_same_outage_state = [
            new_primary_edge_full_info
        ]

        ticket_id = 12345
        ticket_creation_response = {
            'request_id': uuid_,
            'body': ticket_id,
            'status': 472,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=ticket_creation_response)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(return_value=edges_in_same_outage_state)
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_primary_edges_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(
            return_value=all_links_grouped_by_edge_with_ha_info
        )

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._append_triage_note = CoroutineMock()
        outage_monitor._change_ticket_severity = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, edge_primary_serial)
        outage_monitor._change_ticket_severity.assert_awaited_once_with(
            ticket_id=ticket_id,
            edge_status=links_grouped_by_primary_edge_with_ha_info,
            check_ticket_tasks=True,
        )
        outage_monitor._append_triage_note.assert_awaited_once_with(
            ticket_id, cached_edge_primary, links_grouped_by_primary_edge_with_ha_info, outage_type,
            is_reopen_note=True,
        )
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_edges_still_in_same_outage_state_and_ticket_creation_returning_473_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        edge_primary_serial = 'VC1234567'
        edge_standby_serial = 'VC5678901'

        edge_primary_initial_state = 'OFFLINE'
        edge_standby_initial_state_normalized = 'OFFLINE'

        edge_primary_new_state = 'OFFLINE'
        edge_standby_new_state_raw = 'FAILED'
        edge_standby_new_state_normalized = 'OFFLINE'

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_full_id = {'host': velocloud_host, 'enterprise_id': enterprise_id, 'edge_id': edge_id}
        logical_id_list = [{'interface_name': 'REX', 'logical_id': '123'}]

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        cached_edge_primary = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_primary_serial,
            'ha_serial_number': edge_standby_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }
        cached_edge_standby = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_standby_serial,
            'ha_serial_number': edge_primary_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list,
        }

        edge_link_1_info = {
            # Some fields omitted for simplicity
            'interface': 'REX',
            'linkState': 'STABLE',
            'linkId': 5293,
        }
        edge_primary_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_initial_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'edgeHAState': edge_standby_initial_state_normalized,
            'edgeIsHAPrimary': True,
        }
        edge_with_links_primary = {
            **edge_primary_info,
            'links': [
                edge_link_1_info,
            ],
        }

        edge_primary_full_info = {
            'cached_info': cached_edge_primary,
            'status': edge_with_links_primary,
        }
        outage_edges = [
            edge_primary_full_info,
        ]

        edge_primary_network_enterprises = {
            # Some fields omitted for simplicity
            'edgeState': edge_primary_new_state,
            'enterpriseId': enterprise_id,
            'haSerialNumber': edge_standby_serial,
            'haState': edge_standby_new_state_raw,
            'id': edge_id,
            'name': 'Big Boss',
            'serialNumber': edge_primary_serial,
        }
        edges_network_enterprises = [
            edge_primary_network_enterprises,
        ]
        network_enterprises_response = {
            'body': edges_network_enterprises,
            'status': 200,
        }

        new_links_with_primary_edge_info = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            **edge_link_1_info,
        }
        new_links_with_edge_info = [
            new_links_with_primary_edge_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

        new_links_grouped_by_primary_edge = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': edge_primary_new_state,
            'edgeId': edge_id,
            'edgeSerialNumber': edge_primary_serial,
            'edgeHASerialNumber': edge_standby_serial,
            'links': [
                edge_link_1_info
            ],
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_primary_edge,
        ]

        links_grouped_by_primary_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeHAState': edge_standby_new_state_normalized,
            'edgeIsHAPrimary': True,
        }
        links_grouped_by_standby_edge_with_ha_info = {
            **new_links_grouped_by_primary_edge,
            'edgeSerialNumber': edge_standby_serial,
            'edgeState': edge_standby_new_state_normalized,
            'edgeHASerialNumber': edge_primary_serial,
            'edgeHAState': edge_primary_new_state,
            'edgeIsHAPrimary': False,
        }
        links_grouped_by_primary_edges_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
        ]
        all_links_grouped_by_edge_with_ha_info = [
            links_grouped_by_primary_edge_with_ha_info,
            links_grouped_by_standby_edge_with_ha_info,
        ]

        new_primary_edge_full_info = {
            'cached_info': cached_edge_primary,
            'status': links_grouped_by_primary_edge_with_ha_info,
        }
        new_standby_edge_full_info = {
            'cached_info': cached_edge_standby,
            'status': links_grouped_by_standby_edge_with_ha_info,
        }
        new_edges_full_info = [
            new_primary_edge_full_info,
            new_standby_edge_full_info,
        ]

        edges_in_same_outage_state = [
            new_primary_edge_full_info
        ]

        ticket_id = 12345
        ticket_creation_response = {
            'request_id': uuid_,
            'body': ticket_id,
            'status': 473,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.get_network_enterprises = CoroutineMock(return_value=network_enterprises_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=ticket_creation_response)

        outage_repository = Mock()
        outage_repository.filter_edges_by_outage_type = Mock(return_value=edges_in_same_outage_state)
        outage_repository.is_edge_up = Mock(return_value=False)

        ha_repository = Mock()
        ha_repository.map_edges_with_ha_info = Mock(return_value=links_grouped_by_primary_edges_with_ha_info)
        ha_repository.get_edges_with_standbys_as_standalone_edges = Mock(
            return_value=all_links_grouped_by_edge_with_ha_info
        )

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._append_triage_note = CoroutineMock()
        outage_monitor._change_ticket_severity = CoroutineMock()

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges, outage_type)

        bruin_repository.create_outage_ticket.assert_awaited_once_with(client_id, edge_primary_serial)
        outage_monitor._change_ticket_severity.assert_awaited_once_with(
            ticket_id=ticket_id,
            edge_status=links_grouped_by_primary_edge_with_ha_info,
            check_ticket_tasks=False,
        )
        outage_monitor._append_triage_note.assert_awaited_once_with(
            ticket_id, cached_edge_primary, links_grouped_by_primary_edge_with_ha_info, outage_type,
        )
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_triage_note_with_retrieval_of_edge_events_returning_non_2xx_status_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_serial = 'VC1234567'
        edge_ha_serial = 'VC9999999'

        ticket_id = 12345
        edge_full_id = {
            "host": velocloud_host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        edge_status = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': edge_ha_serial,
            'links': [
                {
                    # Some fields omitted for simplicity
                    'interface': 'REX',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                }
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
        }

        edge_events_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._append_triage_note(ticket_id, cached_edge, edge_status, outage_type)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        bruin_repository.get_ticket_details.assert_not_awaited()
        triage_repository.build_triage_note.assert_not_called()

    @pytest.mark.asyncio
    async def append_triage_note_with_events_sorted_before_building_triage_note_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_serial = 'VC1234567'
        edge_ha_serial = 'VC9999999'

        ticket_id = 12345
        edge_full_id = {
            "host": velocloud_host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        edge_status = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': edge_ha_serial,
            'links': [
                {
                    # Some fields omitted for simplicity
                    'interface': 'REX',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                }
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:30:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:40:00+00:00',
            'message': 'Link GE1 is no longer DEAD'
        }
        events = [event_1, event_2, event_3]
        events_sorted_by_event_time = [event_3, event_2, event_1]

        edge_events_response = {
            'body': events,
            'status': 200,
        }

        ticket_detail_1 = {
            'detailID': 12345,
            'detailValue': edge_serial,
        }
        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    ticket_detail_1,
                ],
                'ticketNotes': [],
            },
            'status': 200,
        }

        ticket_detail_object = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail_1,
        }

        triage_note = 'This is a triage note'

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        triage_repository = Mock()
        triage_repository.build_triage_note = Mock(return_value=triage_note)

        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.append_triage_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'dev'):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._append_triage_note(ticket_id, cached_edge, edge_status, outage_type)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        triage_repository.build_triage_note.assert_called_once_with(
            cached_edge, edge_status, events_sorted_by_event_time, outage_type, is_reopen_note=False,
        )
        bruin_repository.append_triage_note.assert_awaited_with(ticket_detail_object, triage_note)

    @pytest.mark.asyncio
    async def append_triage_note_with_events_error_appending_triage_note_test(self):
        outage_type = Outages.HA_HARD_DOWN  # We can use whatever outage type

        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_serial = 'VC1234567'
        edge_ha_serial = 'VC9999999'

        ticket_id = 12345
        edge_full_id = {
            "host": velocloud_host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }
        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]
        cached_edge = {
            'edge': edge_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        edge_status = {
            # Some fields omitted for simplicity
            'host': velocloud_host,
            'enterpriseId': enterprise_id,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': edge_ha_serial,
            'links': [
                {
                    # Some fields omitted for simplicity
                    'interface': 'REX',
                    'linkState': 'DISCONNECTED',
                    'linkId': 5293,
                }
            ],
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:30:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:40:00+00:00',
            'message': 'Link GE1 is no longer DEAD'
        }
        events = [event_1, event_2, event_3]
        events_sorted_by_event_time = [event_3, event_2, event_1]

        edge_events_response = {
            'body': events,
            'status': 200,
        }

        ticket_detail_1 = {
            'detailID': 12345,
            'detailValue': edge_serial,
        }
        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    ticket_detail_1,
                ],
                'ticketNotes': [],
            },
            'status': 200,
        }

        ticket_detail_object = {
            'ticket_id': ticket_id,
            'ticket_detail': ticket_detail_1,
        }

        triage_note = 'This is a triage note'

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        triage_repository = Mock()
        triage_repository.build_triage_note = Mock(return_value=triage_note)

        metrics_repository = Mock()
        metrics_repository.increment_first_triage_errors = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.append_triage_note = CoroutineMock(return_value=503)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'dev'):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._append_triage_note(ticket_id, cached_edge, edge_status, outage_type)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        triage_repository.build_triage_note.assert_called_once_with(
            cached_edge, edge_status, events_sorted_by_event_time, outage_type, is_reopen_note=False,
        )
        bruin_repository.append_triage_note.assert_awaited_with(ticket_detail_object, triage_note)
        metrics_repository.increment_first_triage_errors.assert_called_once()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_with_failing_reopening_test(self):
        ticket_id = 1234567
        detail_1_id = 9876543
        detail_2_id = 1112223

        host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1

        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC7654321'
        edge_status = {
            'host': host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_id,
            'edgeSerialNumber': serial_number_1,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ],
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
        }
        cached_edge = {
            'edge': {'host': host, 'enterprise_id': enterprise_id, 'edge_id': edge_id},
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': serial_number_1,
            'ha_serial_number': None,
            'bruin_client_info': {
                'client_id': 30000,
                'client_name': 'MetTel',
            },
            'logical_ids': [],
        }
        outage_type = Outages.HARD_DOWN  # We can use whatever outage type

        ticket_details_result = {
            'request_id': uuid_,
            'body': {
                'ticketDetails': [
                    {
                        "detailID": detail_1_id,
                        "detailType": "Repair_WTN",
                        "detailStatus": "R",
                        "detailValue": serial_number_2,
                        "assignedToName": "0",
                        "currentTaskID": None,
                        "currentTaskName": None,
                        "lastUpdatedBy": 0,
                        "lastUpdatedAt": "2020-02-14T12:40:04.69-05:00"
                    },
                    {
                        "detailID": detail_2_id,
                        "detailType": "Repair_WTN",
                        "detailStatus": "R",
                        "detailValue": serial_number_1,
                        "assignedToName": "0",
                        "currentTaskID": None,
                        "currentTaskName": None,
                        "lastUpdatedBy": 0,
                        "lastUpdatedAt": "2020-02-14T12:40:04.69-05:00"
                    }
                ],
            },
            'status': 200,
        }

        reopen_ticket_result = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_result)
        bruin_repository.open_ticket = CoroutineMock(return_value=reopen_ticket_result)
        digi_repository = Mock()
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._append_triage_note = CoroutineMock()

        await outage_monitor._reopen_outage_ticket(ticket_id, edge_status, cached_edge, outage_type)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, detail_2_id)
        outage_monitor._append_triage_note.assert_not_awaited()
        logger.error.assert_called()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_with_successful_reopening_test(self):
        ticket_id = 1234567
        detail_1_id = 9876543
        detail_2_id = 1112223

        host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1

        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC7654321'
        edge_status = {
            'host': host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_id,
            'edgeSerialNumber': serial_number_1,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ],
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
        }
        cached_edge = {
            'edge': {'host': host, 'enterprise_id': enterprise_id, 'edge_id': edge_id},
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': serial_number_1,
            'ha_serial_number': None,
            'bruin_client_info': {
                'client_id': 30000,
                'client_name': 'MetTel',
            },
            'logical_ids': [],
        }
        outage_type = Outages.HARD_DOWN  # We can use whatever outage type

        ticket_details_result = {
            'request_id': uuid_,
            'body': {
                'ticketDetails': [
                    {
                        "detailID": detail_1_id,
                        "detailType": "Repair_WTN",
                        "detailStatus": "R",
                        "detailValue": serial_number_2,
                        "assignedToName": "0",
                        "currentTaskID": None,
                        "currentTaskName": None,
                        "lastUpdatedBy": 0,
                        "lastUpdatedAt": "2020-02-14T12:40:04.69-05:00"
                    },
                    {
                        "detailID": detail_2_id,
                        "detailType": "Repair_WTN",
                        "detailStatus": "R",
                        "detailValue": serial_number_1,
                        "assignedToName": "0",
                        "currentTaskID": None,
                        "currentTaskName": None,
                        "lastUpdatedBy": 0,
                        "lastUpdatedAt": "2020-02-14T12:40:04.69-05:00"
                    },
                ]
            },
            'status': 200,
        }

        reopen_ticket_result = {
            'request_id': uuid_,
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        config = testconfig
        outage_repository = Mock()
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_result)
        bruin_repository.open_ticket = CoroutineMock(return_value=reopen_ticket_result)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._append_triage_note = CoroutineMock()

        await outage_monitor._reopen_outage_ticket(ticket_id, edge_status, cached_edge, outage_type)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, detail_2_id)
        outage_monitor._append_triage_note.assert_awaited_once_with(
            ticket_id, cached_edge, edge_status, outage_type, is_reopen_note=True
        )
        notifications_repository.send_slack_message.assert_called_once_with(
            f'Detail {detail_2_id} of outage ticket {ticket_id} reopened: https://app.bruin.com/t/{ticket_id}'
        )

    def is_detail_resolved_test(self):
        ticket_detail = {
            "detailID": 12345,
            "detailValue": 'VC1234567',
            "detailStatus": "I",
        }
        result = OutageMonitor._is_detail_resolved(ticket_detail)
        assert result is False

        ticket_detail = {
            "detailID": 12345,
            "detailValue": 'VC1234567',
            "detailStatus": "R",
        }
        result = OutageMonitor._is_detail_resolved(ticket_detail)
        assert result is True

    @pytest.mark.asyncio
    async def check_for_digi_reboot_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        success_reboot = {
            'body': 'Success',
            'status': 200
        }
        failed_reboot = {
            'body': 'Failed',
            'status': 400
        }
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]
        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_repository = Mock()
        outage_repository.is_faulty_link = Mock(return_value=True)

        digi_repository = Mock()
        digi_repository.reboot_link = CoroutineMock(side_effect=[success_reboot, failed_reboot])
        digi_repository.get_digi_links = Mock(return_value=digi_list)

        bruin_repository = Mock()
        bruin_repository.append_digi_reboot_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        slack_message = (
            f'DiGi reboot started for faulty edge {edge_1_serial}. Ticket '
            f'details at https://app.bruin.com/t/{ticket_id}.'
        )

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        await outage_monitor._check_for_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                    new_links_grouped_by_edge_1)

        outage_repository.is_faulty_link.assert_has_calls([
            call(new_links_grouped_by_edge_1['links'][0]['linkState']),
            call(new_links_grouped_by_edge_1['links'][1]['linkState'])])

        digi_repository.reboot_link.assert_has_awaits([
            call(edge_1_serial, ticket_id, logical_id_list[1]['logical_id']),
            call(edge_1_serial, ticket_id, logical_id_list[2]['logical_id'])
        ])

        bruin_repository.append_digi_reboot_note.assert_awaited_once_with(ticket_id, edge_1_serial,
                                                                          logical_id_list[1]['interface_name'])
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    def get_last_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        outage_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        result = outage_monitor._get_last_element_matching(iterable=payload, condition=cond)
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

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        bruin_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        outage_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        result = outage_monitor._get_last_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }

        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=30)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            'createdDate': str(ticket_time_stamp)
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        slack_message = f'Forwarding ticket {ticket_id} to Wireless team'

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_task_result_change_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(side_effect=[False, True])

        digi_repository = Mock()
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        task_result = "Wireless Repair Intervention Needed"

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)
        digi_repository.get_interface_name_from_digi_note.assert_has_calls([call(ticket_note_1)])

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        bruin_repository.change_detail_work_queue.assert_awaited_once_with(ticket_id, task_result,
                                                                           serial_number=edge_1_serial,
                                                                           detail_id=outage_ticket_detail_1['detailID'])
        bruin_repository.append_task_result_change_note.assert_awaited_once_with(ticket_id, task_result)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_wrong_interface_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }

        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=30)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            'createdDate': str(ticket_time_stamp)
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}
        success_reboot = {
            'body': 'Success',
            'status': 200
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        slack_message = f'DiGi reboot started for faulty edge {serial_number_1}. Ticket details ' \
                        f'at https://app.bruin.com/t/{ticket_id}.'

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_task_result_change_note = CoroutineMock()
        bruin_repository.append_digi_reboot_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(side_effect=[True, False])

        digi_repository = Mock()
        digi_repository.reboot_link = CoroutineMock(return_value=success_reboot)
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        task_result = "Wireless Repair Intervention Needed"

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)
        digi_repository.get_interface_name_from_digi_note.assert_has_calls([call(ticket_note_1)])

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_task_result_change_note.assert_not_awaited()
        digi_repository.reboot_link.assert_awaited_once(serial_number_1, ticket_id, logical_id_list[1]['logical_id'])
        bruin_repository.append_digi_reboot_note.assert_awaited_once(ticket_id, serial_number_1,
                                                                     logical_id_list[1]['interface_name'])
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_wrong_interface_failed_reboot_request_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }

        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=30)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            'createdDate': str(ticket_time_stamp)
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}
        failed_reboot = {
            'body': 'Failed',
            'status': 400
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        slack_message = f'DiGi reboot started for faulty edge {serial_number_1}. Ticket details ' \
                        f'at https://app.bruin.com/t/{ticket_id}.'

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_task_result_change_note = CoroutineMock()
        bruin_repository.append_digi_reboot_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(side_effect=[True, False])

        digi_repository = Mock()
        digi_repository.reboot_link = CoroutineMock(return_value=failed_reboot)
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        task_result = "Wireless Repair Intervention Needed"

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)
        digi_repository.get_interface_name_from_digi_note.assert_has_calls([call(ticket_note_1)])

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_task_result_change_note.assert_not_awaited()
        digi_repository.reboot_link.assert_awaited_once(serial_number_1, ticket_id, logical_id_list[1]['logical_id'])
        bruin_repository.append_digi_reboot_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_edge_outage_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }

        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=31)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            'createdDate': str(ticket_time_stamp)
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        slack_message = f'Forwarding ticket {ticket_id} to Wireless team'

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_task_result_change_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=True)
        outage_repository.is_faulty_link = Mock(return_value=True)

        digi_repository = Mock()
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        task_result = "Wireless Repair Intervention Needed"

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_not_called()
        digi_repository.get_interface_name_from_digi_note.assert_not_called()

        bruin_repository.get_ticket_details.assert_not_awaited()
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_task_result_change_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_failed_to_change_task_result_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }

        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=30)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            'createdDate': str(ticket_time_stamp)
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 400}

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        slack_message = f'Forwarding ticket {ticket_id} to Wireless team'

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_task_result_change_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(side_effect=[False, True])

        digi_repository = Mock()
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        task_result = "Wireless Repair Intervention Needed"

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)
        digi_repository.get_interface_name_from_digi_note.assert_has_calls([call(ticket_note_1)])

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        bruin_repository.change_detail_work_queue.assert_awaited_once_with(ticket_id, task_result,
                                                                           serial_number=edge_1_serial,
                                                                           detail_id=outage_ticket_detail_1['detailID'])
        bruin_repository.append_task_result_change_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_under_30_mins_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }
        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=29)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            'createdDate': str(ticket_time_stamp)
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        slack_message = f'Forwarding ticket {ticket_id} to Wireless team'

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_task_result_change_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(return_value=True)

        digi_repository = Mock()
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        task_result = "Wireless Repair Intervention Needed"

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        bruin_repository.change_detail_work_queue.assert_not_awaited()

        digi_repository.get_interface_name_from_digi_note.assert_not_called()

        bruin_repository.append_task_result_change_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_failed_rpc_call_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }
        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=30)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            'createdDate': str(ticket_time_stamp)
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': 'Failed',
            'status': 400,
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock()
        bruin_repository.append_task_result_change_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(return_value=True)

        digi_repository = Mock()
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        task_result = "Wireless Repair Intervention Needed"

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        digi_repository.get_interface_name_from_digi_note.assert_not_called()

        bruin_repository.append_task_result_change_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_no_digi_note_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }

        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock()
        bruin_repository.append_task_result_change_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(return_value=True)

        digi_repository = Mock()
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        task_result = "Wireless Repair Intervention Needed"

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                           new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        digi_repository.get_interface_name_from_digi_note.assert_not_called()
        bruin_repository.change_detail_work_queue.assert_not_awaited()

        bruin_repository.append_task_result_change_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_task_result_already_changed_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        task_result = "Wireless Repair Intervention Needed"
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '00:27:04:123'},
                           {'interface_name': 'GE3', 'logical_id': '00:27:04:122'},
                           {'interface_name': 'GE2', 'logical_id': '00:04:2d:123'}]
        digi_list = [logical_id_list[3], logical_id_list[1], logical_id_list[2]]

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }
        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=31)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            "createdDate": str(ticket_time_stamp)
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Task result change\n"
                         f"Changing task result to: {task_result}\n"
                         f"TimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock()
        bruin_repository.append_task_result_change_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(side_effect=[False, True])

        digi_repository = Mock()
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        digi_repository.get_interface_name_from_digi_note.assert_has_calls([call(ticket_note_1)])
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_task_result_change_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def check_for_failed_digi_reboot_no_digi_links_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC9999999'
        task_result = "Wireless Repair Intervention Needed"
        logical_id_list = [{'interface_name': 'test', 'logical_id': '123'},
                           {'interface_name': 'GE1', 'logical_id': '212'},
                           {'interface_name': 'GE3', 'logical_id': '23'},
                           {'interface_name': 'GE2', 'logical_id': '234'}]
        digi_list = []

        ticket_id = 123
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'

        edge_1_enterprise_id = 1
        edge_1_id = 1

        new_links_grouped_by_edge_1 = {
            'host': velocloud_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_1_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'CONNECTED',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_1_id,
            'edgeSerialNumber': edge_1_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE3',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": serial_number_1,
            "detailStatus": "I",
        }
        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=32)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Offline DiGi interface identified for serial: {serial_number_1}\n"
                         f'Interface: GE1\n'
                         f'Automatic reboot attempt started.\n'
                         f"TimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
            'createdDate': str(ticket_time_stamp)

        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": f"#*MetTel's IPA*#\n"
                         f"Task result change\n"
                         f"Changing task result to: {task_result}\n"
                         f"TimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-04 10:18:16-05:00",
            "serviceNumber": [
                serial_number_1,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246617,
            "noteValue": "Some note",
            "serviceNumber": [
                serial_number_2,
            ],
        }
        ticket_note_5 = {
            "noteId": 68246618,
            "noteValue": "Some other note",
            "serviceNumber": [
                serial_number_1,
                serial_number_2,
            ],
        }
        outage_ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
            ticket_note_5,
        ]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        ha_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock()
        bruin_repository.append_task_result_change_note = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.is_faulty_link = Mock(return_value=True)

        digi_repository = Mock()
        digi_repository.get_digi_links = Mock(return_value=digi_list)
        digi_repository.get_interface_name_from_digi_note = Mock(return_value='GE3')

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)

        bruin_repository.get_ticket_details.assert_not_awaited()
        digi_repository.get_interface_name_from_digi_note.assert_not_called()
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_task_result_change_note.assert_not_awaited()

    @pytest.mark.asyncio
    async def schedule_forward_ticket_queue_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345  # Ticket ID
        velocloud_host = 'mettel.velocloud.net'
        edge_serial = 'VC5678901'
        edge_enterprise_id = 3
        edge_id = 1
        edge_status = {
            'host': velocloud_host,
            'enterpriseName': 'Sarif Industries',
            'enterpriseId': edge_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Adam Jensen',
            'edgeState': 'OFFLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'Augmented',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        current_datetime = datetime.now()
        forward_task_run_date = current_datetime + timedelta(
            seconds=outage_monitor._config.MONITOR_CONFIG['jobs_intervals']['forward_to_hnoc'])
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                outage_monitor.schedule_forward_to_hnoc_queue(ticket_id=ticket_id,
                                                              serial_number=serial_number,
                                                              edge_status=edge_status)

        scheduler.add_job.assert_called_once_with(
            outage_monitor.forward_ticket_to_hnoc_queue, 'date',
            kwargs={'ticket_id': ticket_id, 'serial_number': serial_number, 'edge_status': edge_status},
            run_date=forward_task_run_date,
            replace_existing=False,
            id=f'_forward_ticket_{ticket_id}_{serial_number}_to_hnoc',
        )

    @pytest.mark.asyncio
    async def change_detail_work_queue_2xx_status_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345  # Ticket ID
        task_result = 'HNOC Investigate'
        slack_message = (
            f'Detail of ticket {ticket_id} related to serial {serial_number}'
            f' was successfully forwarded to {task_result} queue!'
        )
        change_queue_ticket_response = {
            'body': 'ok',
            'status': 200,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        velocloud_repository = Mock()
        bruin_repository = Mock()
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_queue_ticket_response)
        outage_repository = Mock()
        config = testconfig

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor.change_detail_work_queue(ticket_id, serial_number)

        outage_monitor._bruin_repository.change_detail_work_queue.assert_called_once_with(serial_number=serial_number,
                                                                                          ticket_id=ticket_id,
                                                                                          task_result=task_result)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    @pytest.mark.asyncio
    async def change_detail_work_queue_4xx_status_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345  # Ticket ID
        task_result = 'HNOC Investigate'
        change_queue_ticket_response = {
            'body': 'ko',
            'status': 400,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        velocloud_repository = Mock()
        bruin_repository = Mock()
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_queue_ticket_response)
        outage_repository = Mock()
        config = testconfig

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor.change_detail_work_queue(ticket_id, serial_number)

        outage_monitor._bruin_repository.change_detail_work_queue.assert_called_once_with(serial_number=serial_number,
                                                                                          ticket_id=ticket_id,
                                                                                          task_result=task_result)
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def forward_ticket_to_hnoc_queue_with_faulty_edge_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345  # Ticket ID
        velocloud_host = 'mettel.velocloud.net'
        edge_serial = 'VC5678901'
        edge_enterprise_id = 3
        edge_id = 1
        edge_status = {
            'host': velocloud_host,
            'enterpriseName': 'Sarif Industries',
            'enterpriseId': edge_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Adam Jensen',
            'edgeState': 'OFFLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'Augmented',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        velocloud_repository = Mock()
        bruin_repository = Mock()

        outage_repository = Mock()
        config = testconfig

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._outage_repository.is_faulty_edge = Mock(return_value=True)
        outage_monitor.change_detail_work_queue = CoroutineMock()
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor.forward_ticket_to_hnoc_queue(ticket_id, serial_number, edge_status)

        outage_monitor.change_detail_work_queue.assert_called_once_with(
            serial_number=serial_number,
            ticket_id=ticket_id)

    @pytest.mark.asyncio
    async def forward_ticket_to_hnoc_queue_with_faulty_link_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345  # Ticket ID
        velocloud_host = 'mettel.velocloud.net'
        edge_serial = 'VC5678901'
        edge_enterprise_id = 3
        edge_id = 1
        ticket = {
            'ticketID': 123,
            "clientName": "Sam &amp; Su's Retail Shop 5",
            "category": "",
            "topic": "Add Cloud PBX User License",
            "referenceTicketNumber": 0,
            "ticketStatus": "Resolved",
            "address": {
                "address": "69 Blanchard St",
                "city": "Newark",
                "state": "NJ",
                "zip": "07105-4701",
                "country": "USA"
            },
            "createDate": "4/23/2019 7:59:50 PM",
            "createdBy": "Amulya Bidar Nataraj 113",
            "creationNote": 'null',
            "resolveDate": "4/23/2019 8:00:35 PM",
            "resolvedby": 'null',
            "closeDate": 'null',
            "closedBy": 'null',
            "lastUpdate": 'null',
            "updatedBy": 'null',
            "mostRecentNote": " ",
            "nextScheduledDate": "4/23/2019 4:00:00 AM",
            "flags": "",
            "severity": "100"
        }
        response_overview = {
            'status': 200,
            'body': ticket
        }
        edge_status = {
            'host': velocloud_host,
            'enterpriseName': 'Sarif Industries',
            'enterpriseId': edge_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Adam Jensen',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'Augmented',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        velocloud_repository = Mock()
        bruin_repository = Mock()

        outage_repository = Mock()
        config = testconfig

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_monitor._outage_repository.is_any_link_disconnected = Mock(return_value=True)
        outage_monitor.change_detail_work_queue = CoroutineMock()
        outage_monitor._bruin_repository.get_ticket_overview = CoroutineMock(return_value=response_overview)
        outage_monitor._is_ticket_old_enough = CoroutineMock(return_value=True)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor.forward_ticket_to_hnoc_queue(ticket_id, serial_number, edge_status)

        outage_monitor.change_detail_work_queue.assert_called_once_with(
            serial_number=serial_number,
            ticket_id=ticket_id)

    @pytest.mark.asyncio
    async def forward_ticket_to_hnoc_queue_with_faulty_link_and_ticket_overview_rpc_returning_4xx_test(self):
        serial_number = 'VC1234567'
        ticket_id = 12345  # Ticket ID
        velocloud_host = 'mettel.velocloud.net'
        edge_serial = 'VC5678901'
        edge_enterprise_id = 3
        edge_id = 1
        response_overview = {
            'status': 400,
            'body': []
        }
        edge_status = {
            'host': velocloud_host,
            'enterpriseName': 'Sarif Industries',
            'enterpriseId': edge_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Adam Jensen',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': 'Test Name',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'Augmented',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        velocloud_repository = Mock()
        bruin_repository = Mock()

        outage_repository = Mock()
        config = testconfig

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_monitor.change_detail_work_queue = CoroutineMock()
        outage_monitor._bruin_repository.get_ticket_overview = CoroutineMock(return_value=response_overview)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor.forward_ticket_to_hnoc_queue(ticket_id, serial_number, edge_status)

        outage_monitor.change_detail_work_queue.assert_not_called()

    def is_ticket_old_enough_test(self):
        ticket_creation_date = '9/25/2020 6:31:54 AM'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        outage_repository = Mock()
        bruin_repository = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        forward_link_outage_wait_time = timedelta(seconds=config.MONITOR_CONFIG['forward_link_outage_seconds'])

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + forward_link_outage_wait_time - timedelta(seconds=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._is_ticket_old_enough(ticket_creation_date)
            assert result is False

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + forward_link_outage_wait_time
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._is_ticket_old_enough(ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + forward_link_outage_wait_time + timedelta(seconds=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._is_ticket_old_enough(ticket_creation_date)
            assert result is True

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': 'Test Name',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': 'BYOB 70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        cached_edge = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': edge_serial,
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE1'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }
        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial,
            "detailStatus": "I",
        }
        current_datetime = datetime.now(utc)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                edge_serial,
            ],
            "createdDate": current_datetime,
        }

        outage_ticket_notes = [ticket_note_1]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        ticket = {
            'ticketID': 123,
            "clientName": "Sam &amp; Su's Retail Shop 5",
            "category": "",
            "topic": "Add Cloud PBX User License",
            "referenceTicketNumber": 0,
            "ticketStatus": "Resolved",
            "address": {
                "address": "69 Blanchard St",
                "city": "Newark",
                "state": "NJ",
                "zip": "07105-4701",
                "country": "USA"
            },
            "createDate": "4/23/2019 7:59:50 PM",
            "createdBy": "Amulya Bidar Nataraj 113",
            "creationNote": 'null',
            "resolveDate": "4/23/2019 8:00:35 PM",
            "resolvedby": 'null',
            "closeDate": 'null',
            "closedBy": 'null',
            "lastUpdate": 'null',
            "updatedBy": 'null',
            "mostRecentNote": " ",
            "nextScheduledDate": "4/23/2019 4:00:00 AM",
            "flags": "",
            "severity": "100"
        }
        response_overview = {
            'status': 200,
            'body': ticket
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        slack_message = (
            f'Detail of ticket {ticket_id} related to serial {edge_serial} was successfully forwarded '
            f'to {task_result} queue!'
        )

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_wired_links = Mock(return_value=edge_status['links'])

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor._attempt_forward_to_asr(cached_edge, edge_status, ticket_id)

        outage_repository.is_faulty_edge.assert_called_once_with(edge_status["edgeState"])
        outage_repository.find_disconnected_wired_links.assert_called_once_with(
            edge_status, cached_edge['links_configuration'])

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)

        bruin_repository.change_detail_work_queue.assert_awaited_once_with(ticket_id, task_result,
                                                                           serial_number=edge_serial,
                                                                           detail_id=outage_ticket_detail_1[
                                                                               'detailID'])
        bruin_repository.append_asr_forwarding_note.assert_awaited_once_with(
            ticket_id, [edge_status['links'][0]], edge_serial
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_faulty_edge_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'OFFLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': 'Test Name',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        cached_edge = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': edge_serial,
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE1'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=True)
        outage_repository.find_disconnected_wired_links = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.change_detail_work_queue = CoroutineMock()
        bruin_repository.append_asr_forwarding_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor._attempt_forward_to_asr(cached_edge, edge_status, ticket_id)

        outage_repository.is_faulty_edge.assert_called_once_with(edge_status["edgeState"])
        outage_repository.find_disconnected_wired_links.assert_not_called()

        bruin_repository.get_ticket_details.assert_not_awaited()

        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()

        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_no_wired_links_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': 'Test Name',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        cached_edge = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': edge_serial,
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE1'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_wired_links = Mock(return_value=[])

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.change_detail_work_queue = CoroutineMock()
        bruin_repository.append_asr_forwarding_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor._attempt_forward_to_asr(cached_edge, edge_status, ticket_id)

        outage_repository.is_faulty_edge.assert_called_once_with(edge_status["edgeState"])
        outage_repository.find_disconnected_wired_links.assert_called_once_with(
            edge_status, cached_edge['links_configuration'])

        bruin_repository.get_ticket_details.assert_not_awaited()

        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()

        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_no_whitelist_links_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': 'BYOB 70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': 'customer owned 70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': 'Customer Owned 70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': 'PIAB - 70.59.5.185',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        cached_edge = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': edge_serial,
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE1'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_wired_links = Mock(return_value=edge_status['links'])

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.change_detail_work_queue = CoroutineMock()
        bruin_repository.append_asr_forwarding_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor._attempt_forward_to_asr(cached_edge, edge_status, ticket_id)

        outage_repository.is_faulty_edge.assert_called_once_with(edge_status["edgeState"])
        outage_repository.find_disconnected_wired_links.assert_called_once_with(
            edge_status, cached_edge['links_configuration'])

        bruin_repository.get_ticket_details.assert_not_awaited()

        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()

        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_failed_ticket_details_rpc_call_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': 'Test Name',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        cached_edge = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': edge_serial,
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE1'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }
        ticket_details_response = {
            'body': 'Failed',
            'status': 400,
        }

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_wired_links = Mock(return_value=edge_status['links'])

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock()
        bruin_repository.append_asr_forwarding_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor._attempt_forward_to_asr(cached_edge, edge_status, ticket_id)

        outage_repository.is_faulty_edge.assert_called_once_with(edge_status["edgeState"])
        outage_repository.find_disconnected_wired_links.assert_called_once_with(
            edge_status, cached_edge['links_configuration'])

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)

        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()

        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_already_forwarded_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': 'Test Name',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        cached_edge = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': edge_serial,
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE1'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }
        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial,
            "detailStatus": "I",
        }
        current_datetime = datetime.now(utc)
        ticket_time_stamp = current_datetime - timedelta(minutes=60)

        task_result_note = f"#*MetTel's IPA*#\nStatus of Wired Link GE1 is DISCONNECTED after 1 hour.\n" \
                           f"Moving task to: ASR Investigate\nTimeStamp: {current_datetime}"

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                edge_serial,
            ],
            "createdDate": current_datetime,
        }

        ticket_note_2 = {
            "noteId": 68246614,
            "noteValue": task_result_note,
            "serviceNumber": [
                edge_serial,
            ],
            "createdDate": ticket_time_stamp,
        }

        outage_ticket_notes = [ticket_note_1, ticket_note_2]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        ticket = {
            'ticketID': 123,
            "clientName": "Sam &amp; Su's Retail Shop 5",
            "category": "",
            "topic": "Add Cloud PBX User License",
            "referenceTicketNumber": 0,
            "ticketStatus": "Resolved",
            "address": {
                "address": "69 Blanchard St",
                "city": "Newark",
                "state": "NJ",
                "zip": "07105-4701",
                "country": "USA"
            },
            "createDate": "4/23/2019 7:59:50 PM",
            "createdBy": "Amulya Bidar Nataraj 113",
            "creationNote": 'null',
            "resolveDate": "4/23/2019 8:00:35 PM",
            "resolvedby": 'null',
            "closeDate": 'null',
            "closedBy": 'null',
            "lastUpdate": 'null',
            "updatedBy": 'null',
            "mostRecentNote": " ",
            "nextScheduledDate": "4/23/2019 4:00:00 AM",
            "flags": "",
            "severity": "100"
        }
        response_overview = {
            'status': 200,
            'body': ticket
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_wired_links = Mock(return_value=edge_status['links'])

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor._attempt_forward_to_asr(cached_edge, edge_status, ticket_id)

        outage_repository.is_faulty_edge.assert_called_once_with(edge_status["edgeState"])
        outage_repository.find_disconnected_wired_links.assert_called_once_with(
            edge_status, cached_edge['links_configuration'])

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)

        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()

        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_failed_to_change_task_result_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'links': [
                {
                    'displayName': 'Test Name',
                    'isp': None,
                    'interface': 'GE1',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        cached_edge = {
            'edge': {"host": "mettel.velocloud.net", "enterprise_id": 19, "edge_id": 1919},
            'last_contact': "0000-00-00 00:00:00",
            'logical_ids': "8456-cg76-sdf3-h64j",
            'serial_number': edge_serial,
            'bruin_client_info': {"client_id": 1991, "client_name": "Tet Corporation"},
            'links_configuration':
                [
                    {
                        'interfaces': ['GE1'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }
        outage_ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial,
            "detailStatus": "I",
        }
        current_datetime = datetime.now(utc)

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                edge_serial,
            ],
            "createdDate": current_datetime,
        }

        outage_ticket_notes = [ticket_note_1]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    outage_ticket_detail_1,
                ],
                'ticketNotes': outage_ticket_notes,
            },
            'status': 200,
        }

        ticket = {
            'ticketID': 123,
            "clientName": "Sam &amp; Su's Retail Shop 5",
            "category": "",
            "topic": "Add Cloud PBX User License",
            "referenceTicketNumber": 0,
            "ticketStatus": "Resolved",
            "address": {
                "address": "69 Blanchard St",
                "city": "Newark",
                "state": "NJ",
                "zip": "07105-4701",
                "country": "USA"
            },
            "createDate": "4/23/2019 7:59:50 PM",
            "createdBy": "Amulya Bidar Nataraj 113",
            "creationNote": 'null',
            "resolveDate": "4/23/2019 8:00:35 PM",
            "resolvedby": 'null',
            "closeDate": 'null',
            "closedBy": 'null',
            "lastUpdate": 'null',
            "updatedBy": 'null',
            "mostRecentNote": " ",
            "nextScheduledDate": "4/23/2019 4:00:00 AM",
            "flags": "",
            "severity": "100"
        }
        response_overview = {
            'status': 200,
            'body': ticket
        }

        change_detail_work_queue_response = {'body': "Failed", 'status': 400}

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_wired_links = Mock(return_value=edge_status['links'])

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        await outage_monitor._attempt_forward_to_asr(cached_edge, edge_status, ticket_id)

        outage_repository.is_faulty_edge.assert_called_once_with(edge_status["edgeState"])
        outage_repository.find_disconnected_wired_links.assert_called_once_with(
            edge_status, cached_edge['links_configuration'])

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)

        bruin_repository.change_detail_work_queue.assert_awaited_once_with(ticket_id, task_result,
                                                                           serial_number=edge_serial,
                                                                           detail_id=outage_ticket_detail_1[
                                                                               'detailID'])
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()

        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def change_ticket_severity_with_edge_down_test(self):
        ticket_id = 12345
        edge_status = {
            # Some fields omitted for simplicity
            'edgeState': 'DISCONNECTED',
            'edgeSerialNumber': 'VC1234567',
            'links': [
                # No links specified for simplicity
            ],
        }

        ticket_info = {
            # Some fields omitted for simplicity
            "ticketID": ticket_id,
            "severity": 3,
        }
        get_ticket_response = {
            'body': ticket_info,
            'status': 200,
        }

        target_severity_level = testconfig.MONITOR_CONFIG['severity_by_outage_type']['edge_down']

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_ticket = CoroutineMock(return_value=get_ticket_response)
        bruin_repository.change_ticket_severity_for_offline_edge = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._is_ticket_already_in_severity_level = Mock(return_value=False)

        # check_ticket_tasks is irrelevant for edge outages, so it's safe to set it to False
        await outage_monitor._change_ticket_severity(ticket_id, edge_status, check_ticket_tasks=False)

        bruin_repository.get_ticket.assert_awaited_once_with(ticket_id)
        outage_monitor._is_ticket_already_in_severity_level.assert_called_once_with(ticket_info, target_severity_level)
        bruin_repository.change_ticket_severity_for_offline_edge.assert_awaited_once_with(ticket_id)

    @pytest.mark.asyncio
    async def change_ticket_severity_with_links_down_and_no_check_for_ticket_tasks_test(self):
        ticket_id = 12345

        link_1_interface = 'REX'
        link_2_interface = 'RAY'
        link_3_interface = 'Mk. II'

        link_1 = {
            # Some fields omitted for simplicity
            'interface': link_1_interface,
            'linkState': 'DISCONNECTED',
        }
        link_2 = {
            # Some fields omitted for simplicity
            'interface': link_2_interface,
            'linkState': 'STABLE',
        }
        link_3 = {
            # Some fields omitted for simplicity
            'interface': link_3_interface,
            'linkState': 'DISCONNECTED',
        }
        edge_status = {
            # Some fields omitted for simplicity
            'edgeState': 'ONLINE',
            'edgeSerialNumber': 'VC1234567',
            'links': [
                link_1,
                link_2,
                link_3,
            ],
        }

        disconnected_links = [
            link_1,
            link_3,
        ]
        disconnected_interfaces = [
            link_1_interface,
            link_3_interface,
        ]

        ticket_info = {
            # Some fields omitted for simplicity
            "ticketID": ticket_id,
            "severity": 3,
        }
        get_ticket_response = {
            'body': ticket_info,
            'status': 200,
        }

        target_severity_level = testconfig.MONITOR_CONFIG['severity_by_outage_type']['link_down']

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_links = Mock(return_value=disconnected_links)

        bruin_repository = Mock()
        bruin_repository.get_ticket = CoroutineMock(return_value=get_ticket_response)
        bruin_repository.change_ticket_severity_for_disconnected_links = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._is_ticket_already_in_severity_level = Mock(return_value=False)

        await outage_monitor._change_ticket_severity(ticket_id, edge_status, check_ticket_tasks=False)

        bruin_repository.get_ticket.assert_awaited_once_with(ticket_id)
        outage_monitor._is_ticket_already_in_severity_level.assert_called_once_with(ticket_info, target_severity_level)
        bruin_repository.change_ticket_severity_for_disconnected_links.assert_awaited_once_with(
            ticket_id, disconnected_interfaces
        )

    @pytest.mark.asyncio
    async def change_ticket_severity_with_links_down_and_check_for_ticket_tasks_and_just_one_ticket_task_test(self):
        ticket_id = 12345
        serial_number = 'VC1234567'

        link_1_interface = 'REX'
        link_2_interface = 'RAY'
        link_3_interface = 'Mk. II'

        link_1 = {
            # Some fields omitted for simplicity
            'interface': link_1_interface,
            'linkState': 'DISCONNECTED',
        }
        link_2 = {
            # Some fields omitted for simplicity
            'interface': link_2_interface,
            'linkState': 'STABLE',
        }
        link_3 = {
            # Some fields omitted for simplicity
            'interface': link_3_interface,
            'linkState': 'DISCONNECTED',
        }
        edge_status = {
            # Some fields omitted for simplicity
            'edgeState': 'ONLINE',
            'edgeSerialNumber': serial_number,
            'links': [
                link_1,
                link_2,
                link_3,
            ],
        }

        disconnected_links = [
            link_1,
            link_3,
        ]
        disconnected_interfaces = [
            link_1_interface,
            link_3_interface,
        ]

        ticket_tasks = [
            {
                "detailID": 11111,
                "detailStatus": 'I',
                "detailValue": serial_number,
                # Some fields omitted for simplicity
            }
        ]
        ticket_details_response = {
            'body': {
                'ticketDetails': ticket_tasks,
                'ticketNotes': [],
            },
            'status': 200,
        }

        ticket_info = {
            # Some fields omitted for simplicity
            "ticketID": ticket_id,
            "severity": 3,
        }
        get_ticket_response = {
            'body': ticket_info,
            'status': 200,
        }

        target_severity_level = testconfig.MONITOR_CONFIG['severity_by_outage_type']['link_down']

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_links = Mock(return_value=disconnected_links)

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.get_ticket = CoroutineMock(return_value=get_ticket_response)
        bruin_repository.change_ticket_severity_for_disconnected_links = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._has_ticket_multiple_unresolved_tasks = Mock(return_value=False)
        outage_monitor._is_ticket_already_in_severity_level = Mock(return_value=False)

        await outage_monitor._change_ticket_severity(ticket_id, edge_status, check_ticket_tasks=True)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor._has_ticket_multiple_unresolved_tasks.assert_called_once_with(ticket_tasks)
        bruin_repository.get_ticket.assert_awaited_once_with(ticket_id)
        outage_monitor._is_ticket_already_in_severity_level.assert_called_once_with(ticket_info, target_severity_level)
        bruin_repository.change_ticket_severity_for_disconnected_links.assert_awaited_once_with(
            ticket_id, disconnected_interfaces
        )

    @pytest.mark.asyncio
    async def change_ticket_severity_with_links_down_and_no_check_for_ticket_tasks_and_multiple_ticket_tasks_test(self):
        ticket_id = 12345
        serial_number = 'VC1234567'

        link_1_interface = 'REX'
        link_2_interface = 'RAY'
        link_3_interface = 'Mk. II'

        link_1 = {
            # Some fields omitted for simplicity
            'interface': link_1_interface,
            'linkState': 'DISCONNECTED',
        }
        link_2 = {
            # Some fields omitted for simplicity
            'interface': link_2_interface,
            'linkState': 'STABLE',
        }
        link_3 = {
            # Some fields omitted for simplicity
            'interface': link_3_interface,
            'linkState': 'DISCONNECTED',
        }
        edge_status = {
            # Some fields omitted for simplicity
            'edgeState': 'ONLINE',
            'edgeSerialNumber': serial_number,
            'links': [
                link_1,
                link_2,
                link_3,
            ],
        }

        disconnected_links = [
            link_1,
            link_3,
        ]

        ticket_tasks = [
            {
                "detailID": 11111,
                "detailStatus": 'I',
                "detailValue": serial_number,
                # Some fields omitted for simplicity
            },
            {
                "detailID": 22222,
                "detailStatus": 'I',
                "detailValue": 'VC9999999',
                # Some fields omitted for simplicity
            }
        ]
        ticket_details_response = {
            'body': {
                'ticketDetails': ticket_tasks,
                'ticketNotes': [],
            },
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_links = Mock(return_value=disconnected_links)

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.get_ticket = CoroutineMock()
        bruin_repository.change_ticket_severity_for_disconnected_links = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._has_ticket_multiple_unresolved_tasks = Mock(return_value=True)
        outage_monitor._is_ticket_already_in_severity_level = Mock()

        await outage_monitor._change_ticket_severity(ticket_id, edge_status, check_ticket_tasks=True)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor._has_ticket_multiple_unresolved_tasks.assert_called_once_with(ticket_tasks)
        bruin_repository.get_ticket.assert_not_awaited()
        outage_monitor._is_ticket_already_in_severity_level.assert_not_called()
        bruin_repository.change_ticket_severity_for_disconnected_links.assert_not_awaited()

    @pytest.mark.asyncio
    async def change_ticket_severity_with_links_down_and_no_check_for_ticket_tasks_and_ticket_details_rpc_failure_test(
            self):
        ticket_id = 12345
        serial_number = 'VC1234567'

        link_1_interface = 'REX'
        link_2_interface = 'RAY'
        link_3_interface = 'Mk. II'

        link_1 = {
            # Some fields omitted for simplicity
            'interface': link_1_interface,
            'linkState': 'DISCONNECTED',
        }
        link_2 = {
            # Some fields omitted for simplicity
            'interface': link_2_interface,
            'linkState': 'STABLE',
        }
        link_3 = {
            # Some fields omitted for simplicity
            'interface': link_3_interface,
            'linkState': 'DISCONNECTED',
        }
        edge_status = {
            # Some fields omitted for simplicity
            'edgeState': 'ONLINE',
            'edgeSerialNumber': serial_number,
            'links': [
                link_1,
                link_2,
                link_3,
            ],
        }

        disconnected_links = [
            link_1,
            link_3,
        ]

        ticket_details_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=False)
        outage_repository.find_disconnected_links = Mock(return_value=disconnected_links)

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.get_ticket = CoroutineMock()
        bruin_repository.change_ticket_severity_for_disconnected_links = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._has_ticket_multiple_unresolved_tasks = Mock(return_value=True)
        outage_monitor._is_ticket_already_in_severity_level = Mock()

        await outage_monitor._change_ticket_severity(ticket_id, edge_status, check_ticket_tasks=True)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor._has_ticket_multiple_unresolved_tasks.assert_not_called()
        bruin_repository.get_ticket.assert_not_awaited()
        outage_monitor._is_ticket_already_in_severity_level.assert_not_called()
        bruin_repository.change_ticket_severity_for_disconnected_links.assert_not_awaited()

    @pytest.mark.asyncio
    async def change_ticket_severity_with_retrieval_of_ticket_info_returning_non_2xx_status_test(self):
        ticket_id = 12345
        edge_status = {
            # Some fields omitted for simplicity
            'edgeState': 'DISCONNECTED',
            'edgeSerialNumber': 'VC1234567',
            'links': [
                # No links specified for simplicity
            ],
        }

        get_ticket_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_ticket = CoroutineMock(return_value=get_ticket_response)
        bruin_repository.change_ticket_severity_for_offline_edge = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._is_ticket_already_in_severity_level = Mock()

        await outage_monitor._change_ticket_severity(ticket_id, edge_status, check_ticket_tasks=False)

        bruin_repository.get_ticket.assert_awaited_once_with(ticket_id)
        outage_monitor._is_ticket_already_in_severity_level.assert_not_called()
        bruin_repository.change_ticket_severity_for_offline_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def change_ticket_severity_with_ticket_already_in_target_severity_level_test(self):
        ticket_id = 12345
        edge_status = {
            # Some fields omitted for simplicity
            'edgeState': 'DISCONNECTED',
            'edgeSerialNumber': 'VC1234567',
            'links': [
                # No links specified for simplicity
            ],
        }

        ticket_info = {
            # Some fields omitted for simplicity
            "ticketID": ticket_id,
            "severity": 3,
        }
        get_ticket_response = {
            'body': ticket_info,
            'status': 200,
        }

        target_severity_level = testconfig.MONITOR_CONFIG['severity_by_outage_type']['edge_down']

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(return_value=True)

        bruin_repository = Mock()
        bruin_repository.get_ticket = CoroutineMock(return_value=get_ticket_response)
        bruin_repository.change_ticket_severity_for_offline_edge = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)
        outage_monitor._is_ticket_already_in_severity_level = Mock(return_value=True)

        await outage_monitor._change_ticket_severity(ticket_id, edge_status, check_ticket_tasks=False)

        bruin_repository.get_ticket.assert_awaited_once_with(ticket_id)
        outage_monitor._is_ticket_already_in_severity_level.assert_called_once_with(ticket_info, target_severity_level)
        bruin_repository.change_ticket_severity_for_offline_edge.assert_not_awaited()

    def has_ticket_multiple_unresolved_tasks_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        velocloud_repository = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()
        ha_repository = Mock()
        outage_repository = Mock()
        bruin_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository, ha_repository)

        ticket_tasks = [
            {
                "detailID": 11111,
                "detailStatus": 'I',
                "detailValue": 'VC1234567',
                # Some fields omitted for simplicity
            },
        ]
        result = outage_monitor._has_ticket_multiple_unresolved_tasks(ticket_tasks)
        assert result is False

        ticket_tasks = [
            {
                "detailID": 11111,
                "detailStatus": 'R',
                "detailValue": 'VC1234567',
                # Some fields omitted for simplicity
            },
            {
                "detailID": 22222,
                "detailStatus": 'R',
                "detailValue": 'VC9999999',
                # Some fields omitted for simplicity
            },
        ]
        result = outage_monitor._has_ticket_multiple_unresolved_tasks(ticket_tasks)
        assert result is False

        ticket_tasks = [
            {
                "detailID": 11111,
                "detailStatus": 'I',
                "detailValue": 'VC1234567',
                # Some fields omitted for simplicity
            },
            {
                "detailID": 22222,
                "detailStatus": 'R',
                "detailValue": 'VC9999999',
                # Some fields omitted for simplicity
            },
        ]
        result = outage_monitor._has_ticket_multiple_unresolved_tasks(ticket_tasks)
        assert result is False

        ticket_tasks = [
            {
                "detailID": 11111,
                "detailStatus": 'I',
                "detailValue": 'VC1234567',
                # Some fields omitted for simplicity
            },
            {
                "detailID": 22222,
                "detailStatus": 'I',
                "detailValue": 'VC9999999',
                # Some fields omitted for simplicity
            },
        ]
        result = outage_monitor._has_ticket_multiple_unresolved_tasks(ticket_tasks)
        assert result is True

    def is_ticket_already_in_severity_level_test(self):
        ticket_info = {
            # Some fields omitted for simplicity
            "ticketID": 12345,
            "severity": 3,
        }

        severity_level = 3
        result = OutageMonitor._is_ticket_already_in_severity_level(ticket_info, severity_level)
        assert result is True

        severity_level = 2
        result = OutageMonitor._is_ticket_already_in_severity_level(ticket_info, severity_level)
        assert result is False
