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
from application.repositories import EdgeIdentifier

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

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=get_cache_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=get_cache_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
                                       digi_repository)

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

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=get_cache_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'Augmented',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'DISCONNECTED',
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

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_3_full_info = {
            'cached_info': cached_edge_3,
            'status': links_grouped_by_edge_3,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_3_full_info,
        ]

        is_edge_1_in_outage_state = True
        is_edge_3_in_outage_state = False

        edges_in_outage_state = [
            edge_1_full_info,
        ]
        edges_in_healthy_state = [
            edge_3_full_info,
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
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_3_in_outage_state,
        ])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, links_grouped_by_edge
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_called_once_with(edges_in_outage_state)
        outage_monitor._run_ticket_autoresolve_for_edge.assert_awaited_once_with(edges_in_healthy_state[0])

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

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        outage_monitor._schedule_recheck_job_for_edges.assert_not_called()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def process_velocloud_host_with_just_edges_in_healthy_state_test(self):
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

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_3_full_info = {
            'cached_info': cached_edge_3,
            'status': links_grouped_by_edge_3,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_3_full_info,
        ]

        is_edge_1_in_outage_state = False
        is_edge_3_in_outage_state = False

        edges_in_healthy_state = [
            edge_1_full_info,
            edge_3_full_info,
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
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_3_in_outage_state,
        ])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, links_grouped_by_edge
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_not_called()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_has_awaits([
            call(edges_in_healthy_state[0]),
            call(edges_in_healthy_state[1]),
        ], any_order=True)

    @pytest.mark.asyncio
    async def process_velocloud_host_with_just_edges_in_outage_state_test(self):
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
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'Augmented',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'DISCONNECTED',
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

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_3_full_info = {
            'cached_info': cached_edge_3,
            'status': links_grouped_by_edge_3,
        }
        edges_full_info = [
            edge_1_full_info,
            edge_3_full_info,
        ]

        is_edge_1_in_outage_state = True
        is_edge_3_in_outage_state = True

        edges_in_outage_state = [
            edge_1_full_info,
            edge_3_full_info,
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
        velocloud_repository.group_links_by_edge = Mock(return_value=links_grouped_by_edge)

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_3_in_outage_state,
        ])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=edges_full_info)
        outage_monitor._schedule_recheck_job_for_edges = Mock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._process_velocloud_host(velocloud_host, customer_cache_for_velocloud_host)

        velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=velocloud_host)
        velocloud_repository.group_links_by_edge.assert_called_once_with(links_with_edge_info)
        outage_monitor._map_cached_edges_with_edges_status.assert_called_once_with(
            customer_cache_for_velocloud_host, links_grouped_by_edge
        )

        outage_monitor._schedule_recheck_job_for_edges.assert_called_once_with(edges_in_outage_state)
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

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                outage_monitor._schedule_recheck_job_for_edges(edges)

        expected_run_date = next_run_time + timedelta(seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
        scheduler.add_job.assert_called_once_with(
            outage_monitor._recheck_edges_for_ticket_creation, 'date',
            args=[edges],
            run_date=expected_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f'_ticket_creation_recheck',
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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

        velocloud_repository = Mock()
        velocloud_repository.get_last_down_edge_events = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
            "category": "SD-WAN",
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
            "category": "SD-WAN",
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
            "category": "SD-WAN",
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
            "category": "SD-WAN",
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)

        outage_repository = Mock()
        outage_repository.is_outage_ticket_detail_auto_resolvable = Mock(return_value=False)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
            outage_ticket_notes, serial_number_1, max_autoresolves=3
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
            "category": "SD-WAN",
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
                                       digi_repository)
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
            outage_ticket_notes, serial_number_1, max_autoresolves=3
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
            "category": "SD-WAN",
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.resolve_ticket = CoroutineMock()
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor._is_detail_resolved = Mock(return_value=True)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, serial_number_1, max_autoresolves=3
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
            "category": "SD-WAN",
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor._is_detail_resolved = Mock(return_value=False)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, serial_number_1, max_autoresolves=3
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
            "category": "SD-WAN",
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

        bruin_repository = Mock()
        bruin_repository.get_open_outage_tickets = CoroutineMock(return_value=outage_ticket_response)
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.unpause_ticket_detail = CoroutineMock()
        bruin_repository.resolve_ticket = CoroutineMock(return_value=resolve_outage_ticket_response)
        bruin_repository.append_autoresolve_note_to_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_outage_ticket_detail_auto_resolvable = Mock(return_value=True)

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._autoresolve_serials_whitelist = {serial_number_1}
        outage_monitor._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor._is_detail_resolved = Mock(return_value=False)
        outage_monitor._notify_successful_autoresolve = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._run_ticket_autoresolve_for_edge(edge)

        bruin_repository.get_open_outage_tickets.assert_awaited_once_with(client_id, service_number=serial_number_1)
        outage_monitor._was_ticket_created_by_automation_engine.assert_called_once_with(outage_ticket_1)
        bruin_repository.get_ticket_details.assert_awaited_once_with(outage_ticket_1_id)
        outage_monitor._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes_for_edge, outage_ticket_1_creation_date
        )
        outage_repository.is_outage_ticket_detail_auto_resolvable.assert_called_once_with(
            outage_ticket_notes, serial_number_1, max_autoresolves=3
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

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

        new_now = parse(ticket_creation_date) + timedelta(minutes=59, seconds=59)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date) + timedelta(hours=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            result = outage_monitor._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date) + timedelta(hours=1, seconds=1)
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
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
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
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

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
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
        }

        links_grouped_by_edge_1 = {
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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
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
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }

        outage_edges = [
            edge_1_full_info,
            edge_2_full_info,
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

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._recheck_edges_for_ticket_creation(outage_edges)

        outage_repository.is_there_an_outage.assert_not_called()
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_just_edges_in_healthy_state_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

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
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
        }

        links_grouped_by_edge_1 = {
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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
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
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }

        outage_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        new_links_with_edge_1_info = {
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
        new_links_with_edge_2_info = {
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
        new_links_with_edge_info = [
            new_links_with_edge_1_info,
            new_links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'STABLE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge_2 = {
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
                }
            ]
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_edge_1,
            new_links_grouped_by_edge_2,
        ]

        new_edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': new_links_grouped_by_edge_1,
        }
        new_edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': new_links_grouped_by_edge_2,
        }
        new_edges_full_info = [
            new_edge_1_full_info,
            new_edge_2_full_info,
        ]

        is_edge_1_in_outage_state = False
        is_edge_2_in_outage_state = False

        edges_in_healthy_state = [
            new_edge_1_full_info,
            new_edge_2_full_info,
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
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_2_in_outage_state,
        ])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        await outage_monitor._recheck_edges_for_ticket_creation(outage_edges)

        outage_repository.is_there_an_outage.assert_has_calls([
            call(new_links_grouped_by_edge_1),
            call(new_links_grouped_by_edge_2),
        ])
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_has_awaits([
            call(edges_in_healthy_state[0]),
            call(edges_in_healthy_state[1]),
        ], any_order=True)

    @pytest.mark.asyncio
    async def recheck_edges_with_just_edges_in_outage_state_and_no_production_env_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

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
            'bruin_client_info': bruin_client_info,
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
        }

        links_grouped_by_edge_1 = {
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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
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
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }

        outage_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        new_links_with_edge_1_info = {
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
        new_links_with_edge_2_info = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'DISCONNECTED',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        new_links_with_edge_info = [
            new_links_with_edge_1_info,
            new_links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge_2 = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_edge_1,
            new_links_grouped_by_edge_2,
        ]

        new_edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': new_links_grouped_by_edge_1,
        }
        new_edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': new_links_grouped_by_edge_2,
        }
        new_edges_full_info = [
            new_edge_1_full_info,
            new_edge_2_full_info,
        ]

        is_edge_1_in_outage_state = True
        is_edge_2_in_outage_state = True

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        notifications_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_2_in_outage_state,
        ])

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges)

        outage_repository.is_there_an_outage.assert_has_calls([
            call(new_links_grouped_by_edge_1),
            call(new_links_grouped_by_edge_2),
        ])
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_just_edges_in_outage_state_and_ticket_creation_returning_200_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }
        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }

        links_grouped_by_edge_1 = {
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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
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
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }

        outage_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        new_links_with_edge_1_info = {
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
        new_links_with_edge_2_info = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'DISCONNECTED',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        new_links_with_edge_info = [
            new_links_with_edge_1_info,
            new_links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge_2 = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_edge_1,
            new_links_grouped_by_edge_2,
        ]

        new_edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': new_links_grouped_by_edge_1,
        }
        new_edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': new_links_grouped_by_edge_2,
        }
        new_edges_full_info = [
            new_edge_1_full_info,
            new_edge_2_full_info,
        ]

        is_edge_1_in_outage_state = True
        is_edge_2_in_outage_state = True

        outage_ticket_creation_body_1 = 12345  # Ticket ID
        outage_ticket_creation_status_1 = 200
        outage_ticket_creation_response_1 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_1,
            'status': outage_ticket_creation_status_1,
        }

        outage_ticket_creation_body_2 = 22345  # Ticket ID
        outage_ticket_creation_status_2 = 200
        outage_ticket_creation_response_2 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_2,
            'status': outage_ticket_creation_status_2,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(side_effect=[
            outage_ticket_creation_response_1,
            outage_ticket_creation_response_2,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_2_in_outage_state,
        ])

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._append_triage_note = CoroutineMock()
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._check_for_digi_reboot = CoroutineMock()
        ticket_detail_1 = {
            'detailID': 12345,
            'detailValue': edge_1_serial,
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
        outage_monitor._bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        outage_monitor._bruin_repository.change_detail_work_queue = CoroutineMock(
            return_value={'status': 200, 'body': 'change work'})

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges)

        outage_repository.is_there_an_outage.assert_has_calls([
            call(new_links_grouped_by_edge_1),
            call(new_links_grouped_by_edge_2),
        ])
        bruin_repository.create_outage_ticket.assert_has_awaits([
            call(client_id, edge_1_serial),
            call(client_id, edge_2_serial),
        ])
        outage_monitor._append_triage_note.assert_has_awaits([
            call(outage_ticket_creation_body_1, edge_1_full_id, new_links_grouped_by_edge_1),
            call(outage_ticket_creation_body_2, edge_2_full_id, new_links_grouped_by_edge_2),
        ])
        outage_monitor._check_for_digi_reboot.assert_has_awaits([
            call(outage_ticket_creation_body_1, logical_id_list, edge_1_serial, new_links_grouped_by_edge_1,
                 edge_1_full_id),
            call(outage_ticket_creation_body_2, logical_id_list, edge_2_serial, new_links_grouped_by_edge_2,
                 edge_2_full_id),
        ])
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_just_edges_in_outage_state_and_ticket_creation_returning_409_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }

        links_grouped_by_edge_1 = {
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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
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
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }

        outage_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        new_links_with_edge_1_info = {
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
        new_links_with_edge_2_info = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'DISCONNECTED',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        new_links_with_edge_info = [
            new_links_with_edge_1_info,
            new_links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge_2 = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_edge_1,
            new_links_grouped_by_edge_2,
        ]

        new_edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': new_links_grouped_by_edge_1,
        }
        new_edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': new_links_grouped_by_edge_2,
        }
        new_edges_full_info = [
            new_edge_1_full_info,
            new_edge_2_full_info,
        ]

        is_edge_1_in_outage_state = True
        is_edge_2_in_outage_state = True

        outage_ticket_creation_body_1 = 12345  # Ticket ID
        outage_ticket_creation_status_1 = 409
        outage_ticket_creation_response_1 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_1,
            'status': outage_ticket_creation_status_1,
        }

        outage_ticket_creation_body_2 = 22345  # Ticket ID
        outage_ticket_creation_status_2 = 409
        outage_ticket_creation_response_2 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_2,
            'status': outage_ticket_creation_status_2,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(side_effect=[
            outage_ticket_creation_response_1,
            outage_ticket_creation_response_2,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_2_in_outage_state,
        ])

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._append_triage_note = CoroutineMock()
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._check_for_failed_digi_reboot = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges)

        outage_repository.is_there_an_outage.assert_has_calls([
            call(new_links_grouped_by_edge_1),
            call(new_links_grouped_by_edge_2),
        ])
        bruin_repository.create_outage_ticket.assert_has_awaits([
            call(client_id, edge_1_serial),
            call(client_id, edge_2_serial),
        ])
        outage_monitor._check_for_failed_digi_reboot.assert_has_awaits([
            call(outage_ticket_creation_body_1, logical_id_list, edge_1_serial,
                 new_links_grouped_by_edge_1, edge_1_full_id),
            call(outage_ticket_creation_body_2, logical_id_list, edge_2_serial,
                 new_links_grouped_by_edge_2, edge_2_full_id),
        ])
        outage_monitor._append_triage_note.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_just_edges_in_outage_state_and_ticket_creation_returning_471_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }

        links_grouped_by_edge_1 = {
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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
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
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }

        outage_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        new_links_with_edge_1_info = {
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
        new_links_with_edge_2_info = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'DISCONNECTED',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        new_links_with_edge_info = [
            new_links_with_edge_1_info,
            new_links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge_2 = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_edge_1,
            new_links_grouped_by_edge_2,
        ]

        new_edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': new_links_grouped_by_edge_1,
        }
        new_edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': new_links_grouped_by_edge_2,
        }
        new_edges_full_info = [
            new_edge_1_full_info,
            new_edge_2_full_info,
        ]

        is_edge_1_in_outage_state = True
        is_edge_2_in_outage_state = True

        outage_ticket_creation_body_1 = 12345  # Ticket ID
        outage_ticket_creation_status_1 = 471
        outage_ticket_creation_response_1 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_1,
            'status': outage_ticket_creation_status_1,
        }

        outage_ticket_creation_body_2 = 22345  # Ticket ID
        outage_ticket_creation_status_2 = 471
        outage_ticket_creation_response_2 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_2,
            'status': outage_ticket_creation_status_2,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()
        digi_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(side_effect=[
            outage_ticket_creation_response_1,
            outage_ticket_creation_response_2,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_2_in_outage_state,
        ])

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._append_triage_note = CoroutineMock()
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()
        outage_monitor._check_for_digi_reboot = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges)

        outage_repository.is_there_an_outage.assert_has_calls([
            call(new_links_grouped_by_edge_1),
            call(new_links_grouped_by_edge_2),
        ])
        bruin_repository.create_outage_ticket.assert_has_awaits([
            call(client_id, edge_1_serial),
            call(client_id, edge_2_serial),
        ])
        outage_monitor._append_triage_note.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_has_awaits([
            call(outage_ticket_creation_body_1, new_links_grouped_by_edge_1),
            call(outage_ticket_creation_body_2, new_links_grouped_by_edge_2),
        ])
        outage_monitor._check_for_digi_reboot.assert_has_awaits([
            call(outage_ticket_creation_body_1, logical_id_list, edge_1_serial, new_links_grouped_by_edge_1,
                 edge_1_full_id),
            call(outage_ticket_creation_body_2, logical_id_list, edge_2_serial, new_links_grouped_by_edge_2,
                 edge_2_full_id),
        ])
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_just_edges_in_outage_state_and_ticket_creation_returning_472_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }

        links_grouped_by_edge_1 = {
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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
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
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }

        outage_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        new_links_with_edge_1_info = {
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
        new_links_with_edge_2_info = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'DISCONNECTED',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        new_links_with_edge_info = [
            new_links_with_edge_1_info,
            new_links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge_2 = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_edge_1,
            new_links_grouped_by_edge_2,
        ]

        new_edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': new_links_grouped_by_edge_1,
        }
        new_edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': new_links_grouped_by_edge_2,
        }
        new_edges_full_info = [
            new_edge_1_full_info,
            new_edge_2_full_info,
        ]

        is_edge_1_in_outage_state = True
        is_edge_2_in_outage_state = True

        outage_ticket_creation_body_1 = 12345  # Ticket ID
        outage_ticket_creation_status_1 = 472
        outage_ticket_creation_response_1 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_1,
            'status': outage_ticket_creation_status_1,
        }

        outage_ticket_creation_body_2 = 22345  # Ticket ID
        outage_ticket_creation_status_2 = 472
        outage_ticket_creation_response_2 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_2,
            'status': outage_ticket_creation_status_2,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(side_effect=[
            outage_ticket_creation_response_1,
            outage_ticket_creation_response_2,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_2_in_outage_state,
        ])

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        digi_repository = Mock()
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._append_triage_note = CoroutineMock()
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._post_note_in_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges)

        outage_repository.is_there_an_outage.assert_has_calls([
            call(new_links_grouped_by_edge_1),
            call(new_links_grouped_by_edge_2),
        ])
        bruin_repository.create_outage_ticket.assert_has_awaits([
            call(client_id, edge_1_serial),
            call(client_id, edge_2_serial),
        ])
        outage_monitor._append_triage_note.assert_not_awaited()
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._post_note_in_outage_ticket.assert_has_awaits([
            call(outage_ticket_creation_body_1, new_links_grouped_by_edge_1),
            call(outage_ticket_creation_body_2, new_links_grouped_by_edge_2),
        ])
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_edges_with_just_edges_in_outage_state_and_ticket_creation_returning_473_test(self):
        velocloud_host = 'mettel.velocloud.net'

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC5678901'

        edge_1_enterprise_id = 1
        edge_1_id = 1
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}

        edge_2_enterprise_id = 3
        edge_2_id = 1
        edge_2_full_id = {'host': velocloud_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        client_id = 9994
        bruin_client_info = {
            'client_id': client_id,
            'client_name': 'METTEL/NEW YORK',
        }

        logical_id_list = [{'interface_name': 'GE1', 'logical_id': '123'}]

        cached_edge_1 = {
            'edge': edge_1_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_1_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }
        cached_edge_2 = {
            'edge': edge_2_full_id,
            'last_contact': '2020-08-17T02:23:59',
            'serial_number': edge_2_serial,
            'bruin_client_info': bruin_client_info,
            'logical_ids': logical_id_list
        }

        links_grouped_by_edge_1 = {
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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
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
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': links_grouped_by_edge_1,
        }
        edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': links_grouped_by_edge_2,
        }

        outage_edges = [
            edge_1_full_info,
            edge_2_full_info,
        ]

        new_links_with_edge_1_info = {
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
        new_links_with_edge_2_info = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'DISCONNECTED',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        new_links_with_edge_info = [
            new_links_with_edge_1_info,
            new_links_with_edge_2_info,
        ]
        links_with_edge_info_response = {
            'body': new_links_with_edge_info,
            'status': 200,
        }

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
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge_2 = {
            'host': velocloud_host,
            'enterpriseName': 'Aperture Science',
            'enterpriseId': edge_2_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'GladOS',
            'edgeState': 'OFFLINE',
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
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }
        new_links_grouped_by_edge = [
            new_links_grouped_by_edge_1,
            new_links_grouped_by_edge_2,
        ]

        new_edge_1_full_info = {
            'cached_info': cached_edge_1,
            'status': new_links_grouped_by_edge_1,
        }
        new_edge_2_full_info = {
            'cached_info': cached_edge_2,
            'status': new_links_grouped_by_edge_2,
        }
        new_edges_full_info = [
            new_edge_1_full_info,
            new_edge_2_full_info,
        ]

        is_edge_1_in_outage_state = True
        is_edge_2_in_outage_state = True

        outage_ticket_creation_body_1 = 12345  # Ticket ID
        outage_ticket_creation_status_1 = 473
        outage_ticket_creation_response_1 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_1,
            'status': outage_ticket_creation_status_1,
        }

        outage_ticket_creation_body_2 = 22345  # Ticket ID
        outage_ticket_creation_status_2 = 473
        outage_ticket_creation_response_2 = {
            'request_id': uuid_,
            'body': outage_ticket_creation_body_2,
            'status': outage_ticket_creation_status_2,
        }

        event_bus = Mock()
        scheduler = Mock()
        logger = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_links_with_edge_info = CoroutineMock(return_value=links_with_edge_info_response)
        velocloud_repository.group_links_by_edge = Mock(return_value=new_links_grouped_by_edge)

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(side_effect=[
            outage_ticket_creation_response_1,
            outage_ticket_creation_response_2,
        ])

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_repository = Mock()
        outage_repository.is_there_an_outage = Mock(side_effect=[
            is_edge_1_in_outage_state,
            is_edge_2_in_outage_state,
        ])

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        digi_repository = Mock()
        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._map_cached_edges_with_edges_status = Mock(return_value=new_edges_full_info)
        outage_monitor._append_triage_note = CoroutineMock()
        outage_monitor._reopen_outage_ticket = CoroutineMock()
        outage_monitor._run_ticket_autoresolve_for_edge = CoroutineMock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_edges_for_ticket_creation(outage_edges)

        outage_repository.is_there_an_outage.assert_has_calls([
            call(new_links_grouped_by_edge_1),
            call(new_links_grouped_by_edge_2),
        ])
        bruin_repository.create_outage_ticket.assert_has_awaits([
            call(client_id, edge_1_serial),
            call(client_id, edge_2_serial),
        ])
        outage_monitor._append_triage_note.assert_has_awaits([
            call(outage_ticket_creation_body_1, edge_1_full_id, new_links_grouped_by_edge_1),
            call(outage_ticket_creation_body_2, edge_2_full_id, new_links_grouped_by_edge_2),
        ])
        outage_monitor._reopen_outage_ticket.assert_not_awaited()
        outage_monitor._run_ticket_autoresolve_for_edge.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_triage_note_with_retrieval_of_edge_events_returning_non_2xx_status_test(self):
        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_serial = 'VC1234567'

        ticket_id = 12345
        edge_full_id = {
            "host": velocloud_host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }
        edge_status = {
            'host': velocloud_host,
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
            'edgeSerialNumber': edge_serial,
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
            ]
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

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        bruin_repository.get_ticket_details.assert_not_awaited()
        triage_repository.build_triage_note.assert_not_called()

    @pytest.mark.asyncio
    async def append_triage_note_with_no_edge_events_test(self):
        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_serial = 'VC1234567'

        ticket_id = 12345
        edge_full_id = {
            "host": velocloud_host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }
        edge_status = {
            'host': velocloud_host,
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
            'edgeSerialNumber': edge_serial,
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
            ]
        }

        edge_events_response = {
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
        customer_cache_repository = Mock()
        digi_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_edge_events = CoroutineMock(return_value=edge_events_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        bruin_repository.get_ticket_details.assert_not_awaited()
        triage_repository.build_triage_note.assert_not_called()

    @pytest.mark.asyncio
    async def append_triage_note_with_events_sorted_before_building_triage_note_test(self):
        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_serial = 'VC1234567'

        ticket_id = 12345
        edge_full_id = {
            "host": velocloud_host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }
        edge_status = {
            'host': velocloud_host,
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
            'edgeSerialNumber': edge_serial,
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
            ]
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
                                       digi_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        triage_repository.build_triage_note.assert_called_once_with(
            edge_full_id, edge_status, events_sorted_by_event_time
        )
        bruin_repository.append_triage_note.assert_awaited_with(ticket_detail_object, triage_note)

    @pytest.mark.asyncio
    async def append_triage_note_with_events_error_appending_triage_note_test(self):
        velocloud_host = 'mettel.velocloud.net'
        enterprise_id = 1
        edge_id = 1
        edge_serial = 'VC1234567'

        ticket_id = 12345
        edge_full_id = {
            "host": velocloud_host,
            "enterprise_id": enterprise_id,
            "edge_id": edge_id,
        }
        edge_status = {
            'host': velocloud_host,
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
            'edgeSerialNumber': edge_serial,
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
            ]
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
                                       digi_repository)

        current_datetime = datetime.now()
        past_moment_for_events_lookup = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'dev'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
                await outage_monitor._append_triage_note(ticket_id, edge_full_id, edge_status)

        velocloud_repository.get_last_edge_events.assert_awaited_once_with(
            edge_full_id, since=past_moment_for_events_lookup
        )
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        triage_repository.build_triage_note.assert_called_once_with(
            edge_full_id, edge_status, events_sorted_by_event_time
        )
        bruin_repository.append_triage_note.assert_awaited_with(ticket_detail_object, triage_note)
        metrics_repository.increment_first_triage_errors.assert_called_once()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_with_failing_reopening_test(self):
        ticket_id = 1234567
        detail_1_id = 9876543
        detail_2_id = 1112223

        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC7654321'
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
            ]
        }

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

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

        await outage_monitor._reopen_outage_ticket(ticket_id, edge_status)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, detail_2_id)
        logger.error.assert_called()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_with_successful_reopening_test(self):
        ticket_id = 1234567
        detail_1_id = 9876543
        detail_2_id = 1112223

        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC7654321'
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
            ]
        }

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

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_result)
        bruin_repository.open_ticket = CoroutineMock(return_value=reopen_ticket_result)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._post_note_in_outage_ticket = CoroutineMock()

        await outage_monitor._reopen_outage_ticket(ticket_id, edge_status)

        outage_monitor._post_note_in_outage_ticket.assert_called_once_with(ticket_id, edge_status)
        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, detail_2_id)
        notifications_repository.send_slack_message.assert_called_once_with(
            f'Detail {detail_2_id} of outage ticket {ticket_id} reopened: https://app.bruin.com/t/{ticket_id}'
        )

    @pytest.mark.asyncio
    async def post_note_in_outage_ticket_with_no_outage_causes_test(self):
        ticket_id = 1234567

        serial_number = 'VC1234567'
        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'FAKE STATE',
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
                    'linkState': 'FAKE STATE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'FAKE STATE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'FAKE STATE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'FAKE STATE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_causes = None
        ticket_note_outage_causes = 'Outage causes: Could not determine causes.'

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

        bruin_repository = Mock()
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(
            ticket_id, serial_number, ticket_note_outage_causes
        )

    @pytest.mark.asyncio
    async def post_note_in_outage_ticket_with_outage_causes_and_only_faulty_edge_test(self):
        ticket_id = 1234567

        serial_number = 'VC1234567'
        edge_state = 'OFFLINE'
        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_state,
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
                    'linkState': 'STABLE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'FAKE STATE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'FAKE STATE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_causes = {'edge': edge_state}

        ticket_note_outage_causes = f'Outage causes: Edge was {edge_state}.'

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

        bruin_repository = Mock()
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(
            ticket_id, serial_number, ticket_note_outage_causes
        )

    @pytest.mark.asyncio
    async def post_note_in_outage_ticket_with_outage_causes_and_only_faulty_links_test(self):
        ticket_id = 1234567

        link_1_interface = 'REX'
        link_2_interface = 'RAY'
        links_state = 'DISCONNECTED'
        serial_number = 'VC1234567'
        edge_status = {
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
                    'interface': link_1_interface,
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': links_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': links_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': link_2_interface,
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': links_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': links_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_causes = {'links': {link_1_interface: links_state, link_2_interface: links_state}}

        ticket_note_outage_causes = (
            f'Outage causes: Link {link_1_interface} was {links_state}. Link {link_2_interface} was {links_state}.'
        )

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

        bruin_repository = Mock()
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(
            ticket_id, serial_number, ticket_note_outage_causes
        )

    @pytest.mark.asyncio
    async def post_note_in_outage_ticket_with_outage_causes_and_faulty_edge_and_faulty_links_test(self):
        ticket_id = 1234567

        edge_state = 'OFFLINE'
        link_1_interface = 'REX'
        link_2_interface = 'RAY'
        links_state = 'DISCONNECTED'
        serial_number = 'VC1234567'
        edge_status = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_state,
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
                    'interface': link_1_interface,
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': links_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': links_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': link_2_interface,
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': links_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': links_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        outage_causes = {
            'edge': edge_state,
            'links': {link_1_interface: links_state, link_2_interface: links_state}
        }
        ticket_note_outage_causes = (
            f'Outage causes: Edge was {edge_state}. '
            f'Link {link_1_interface} was {links_state}. Link {link_2_interface} was {links_state}.'
        )

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

        bruin_repository = Mock()
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        outage_monitor._get_outage_causes = Mock(return_value=outage_causes)

        await outage_monitor._post_note_in_outage_ticket(ticket_id, edge_status)

        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(
            ticket_id, serial_number, ticket_note_outage_causes
        )

    def get_outage_causes_test(self):
        edge_1_state = 'CONNECTED'
        edge_1_link_1_state = edge_1_link_2_state = 'STABLE'
        edge_status_1 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
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
                    'linkState': edge_1_link_1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': edge_1_link_1_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_1_link_2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': edge_1_link_2_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        edge_2_state = 'OFFLINE'
        edge_2_link_1_state = edge_2_link_2_state = 'DISCONNECTED'
        edge_status_2 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_2_state,
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
                    'linkState': edge_2_link_1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': edge_2_link_1_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_2_link_2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': edge_2_link_2_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

        edge_3_state = 'OFFLINE'
        edge_3_link_1_state = 'STABLE'
        edge_3_link_2_state = 'DISCONNECTED'
        edge_status_3 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_3_state,
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
                    'linkState': edge_3_link_1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': edge_3_link_1_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'displayName': '70.59.5.185',
                    'isp': None,
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_3_link_2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': edge_3_link_2_state,
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                }
            ]
        }

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
        digi_repository = Mock()

        outage_repository = Mock()
        outage_repository.is_faulty_edge = Mock(side_effect=[False, True, True])
        outage_repository.is_faulty_link = Mock(side_effect=[False, False, True, True, False, True])

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

        result = outage_monitor._get_outage_causes(edge_status_1)
        assert result is None

        result = outage_monitor._get_outage_causes(edge_status_2)
        assert result == {'edge': 'OFFLINE', 'links': {'REX': edge_2_link_1_state, 'RAY': edge_2_link_2_state}}

        result = outage_monitor._get_outage_causes(edge_status_3)
        assert result == {'edge': 'OFFLINE', 'links': {'RAY': edge_2_link_2_state}}

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

        edge_identifier = EdgeIdentifier(**edge_1_full_id)

        slack_message = (
            f'DiGi reboot started for faulty edge {edge_identifier}. Ticket '
            f'details at https://app.bruin.com/t/{ticket_id}.'
        )

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)
        await outage_monitor._check_for_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                    new_links_grouped_by_edge_1, edge_1_full_id)

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

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, outage_repository,
                                       bruin_repository, velocloud_repository, notifications_repository,
                                       triage_repository, customer_cache_repository, metrics_repository,
                                       digi_repository)

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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)
        digi_repository.get_interface_name_from_digi_note.assert_has_calls([call(ticket_note_1)])

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        bruin_repository.change_detail_work_queue.assert_awaited_once_with(edge_1_serial, ticket_id,
                                                                           outage_ticket_detail_1['detailID'],
                                                                           task_result)
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
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}
        edge_identifier = EdgeIdentifier(**edge_1_full_id)

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

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        slack_message = f'DiGi reboot started for faulty edge {edge_identifier}. Ticket details ' \
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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

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
        edge_1_full_id = {'host': velocloud_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}
        edge_identifier = EdgeIdentifier(**edge_1_full_id)

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

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()
        slack_message = f'DiGi reboot started for faulty edge {edge_identifier}. Ticket details ' \
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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

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

        change_detail_work_queue_response = {'body': "Success", 'status': 400}

        logger = Mock()
        scheduler = Mock()
        event_bus = Mock()
        config = testconfig
        velocloud_repository = Mock()
        triage_repository = Mock()
        metrics_repository = Mock()
        customer_cache_repository = Mock()

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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)
        digi_repository.get_interface_name_from_digi_note.assert_has_calls([call(ticket_note_1)])

        bruin_repository.get_ticket_details.assert_has_awaits([call(ticket_id)])
        bruin_repository.change_detail_work_queue.assert_awaited_once_with(edge_1_serial, ticket_id,
                                                                           outage_ticket_detail_1['detailID'],
                                                                           task_result)
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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

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
                                       digi_repository)
        await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                           new_links_grouped_by_edge_1, edge_1_full_id)

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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

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
                                       digi_repository)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            await outage_monitor._check_for_failed_digi_reboot(ticket_id, logical_id_list, edge_1_serial,
                                                               new_links_grouped_by_edge_1, edge_1_full_id)

        digi_repository.get_digi_links.assert_called_once_with(logical_id_list)

        bruin_repository.get_ticket_details.assert_not_awaited()
        digi_repository.get_interface_name_from_digi_note.assert_not_called()
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_task_result_change_note.assert_not_awaited()
