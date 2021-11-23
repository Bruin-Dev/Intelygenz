from collections import OrderedDict
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from application.actions.bouncing_detector import BouncingDetector
from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import bouncing_detector as bouncing_detector_module
from config import testconfig


class TestBouncingDetector:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        assert bouncing_detector._event_bus == event_bus
        assert bouncing_detector._logger == logger
        assert bouncing_detector._scheduler == scheduler
        assert bouncing_detector._config == config
        assert bouncing_detector._bruin_repository == bruin_repository
        assert bouncing_detector._velocloud_repository == velocloud_repository
        assert bouncing_detector._customer_cache_repository == customer_cache_repository
        assert bouncing_detector._notifications_repository == notifications_repository

    @pytest.mark.asyncio
    async def start_bouncing_detector_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(bouncing_detector_module, 'datetime', new=datetime_mock):
            with patch.object(bouncing_detector_module, 'timezone', new=Mock()):
                await bouncing_detector.start_bouncing_detector_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            bouncing_detector._bouncing_detector_process, 'interval',
            minutes=testconfig.BOUNCING_DETECTOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=next_run_time,
            replace_existing=True,
            id='_bouncing_detector',
        )

    @pytest.mark.asyncio
    async def start_bouncing_detector_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(bouncing_detector_module, 'datetime', new=datetime_mock):
            with patch.object(bouncing_detector_module, 'timezone', new=Mock()):
                await bouncing_detector.start_bouncing_detector_job()

        scheduler.add_job.assert_called_once_with(
            bouncing_detector._bouncing_detector_process, 'interval',
            minutes=testconfig.BOUNCING_DETECTOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=undefined,
            replace_existing=True,
            id='_bouncing_detector',
        )

    @pytest.mark.asyncio
    async def bouncing_detector_process_ok_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        cached_edge = {
                          'edge': edge_full_id,
                          'edge_name': 'test-name',
                          'serial_number': 'VC1234567',
                          'last_contact': '2020-08-27T15:25:42.000',
                          'logical_ids': ['logical_ids'],
                          'links_configuration': ['link_configuaration'],
                          'bruin_client_info': {
                              'client_id': 12345,
                              'client_name': 'Aperture Science',
                          }
                      },
        get_cache_response = {
            'request_id': uuid(),
            'body': [
                cached_edge
            ],
            'status': 200,
        }

        link_metric_response = {
            'request_id': uuid(),
            'body': [
                {
                    'host': 'some-host',
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

        enterprise_to_edge_info = {
            1: [cached_edge]
        }
        events_by_serial = {
            'VC1234567': [
                {
                    'event': 'LINK_DEAD',
                    'category': 'NETWORK',
                    'eventTime': '2019-07-30 07:38:00+00:00',
                    'message': 'GE2 dead'
                }
            ]
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_link_metrics = CoroutineMock(return_value=link_metric_response)

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=get_cache_response)

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        bouncing_detector._get_enterprise_to_cached_info_dict = Mock(return_value=enterprise_to_edge_info)
        bouncing_detector._get_events_by_serial_dict = CoroutineMock(return_value=events_by_serial)
        bouncing_detector._check_for_bouncing_events = CoroutineMock()

        await bouncing_detector._bouncing_detector_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        velocloud_repository.get_last_link_metrics.assert_awaited_once()

        bouncing_detector._get_enterprise_to_cached_info_dict.assert_called_once()
        bouncing_detector._get_events_by_serial_dict.assert_awaited_once_with(enterprise_to_edge_info)
        bouncing_detector._check_for_bouncing_events.assert_awaited_once_with(events_by_serial)

    @pytest.mark.asyncio
    async def bouncing_detector_process_customer_cache_return_202_test(self):
        get_cache_response = {
            'request_id': uuid(),
            'body': 'Failed',
            'status': 202,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_link_metrics = CoroutineMock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=get_cache_response)

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        bouncing_detector._get_enterprise_to_cached_info_dict = Mock()
        bouncing_detector._get_events_by_serial_dict = CoroutineMock()
        bouncing_detector._check_for_bouncing_events = CoroutineMock()

        await bouncing_detector._bouncing_detector_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        velocloud_repository.get_last_link_metrics.assert_not_awaited()

        bouncing_detector._get_enterprise_to_cached_info_dict.assert_not_called()
        bouncing_detector._get_events_by_serial_dict.assert_not_awaited()
        bouncing_detector._check_for_bouncing_events.assert_not_awaited()

    @pytest.mark.asyncio
    async def bouncing_detector_process_customer_empty_cache_test(self):
        get_cache_response = {
            'request_id': uuid(),
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_link_metrics = CoroutineMock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=get_cache_response)

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        bouncing_detector._get_enterprise_to_cached_info_dict = Mock()
        bouncing_detector._get_events_by_serial_dict = CoroutineMock()
        bouncing_detector._check_for_bouncing_events = CoroutineMock()

        await bouncing_detector._bouncing_detector_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        velocloud_repository.get_last_link_metrics.assert_not_awaited()

        bouncing_detector._get_enterprise_to_cached_info_dict.assert_not_called()
        bouncing_detector._get_events_by_serial_dict.assert_not_awaited()
        bouncing_detector._check_for_bouncing_events.assert_not_awaited()

    @pytest.mark.asyncio
    async def bouncing_detector_process_failed_link_metrics_test(self):
        edge_full_id = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}

        cached_edge = {
                          'edge': edge_full_id,
                          'edge_name': 'test-name',
                          'serial_number': 'VC1234567',
                          'last_contact': '2020-08-27T15:25:42.000',
                          'logical_ids': ['logical_ids'],
                          'links_configuration': ['link_configuaration'],
                          'bruin_client_info': {
                              'client_id': 12345,
                              'client_name': 'Aperture Science',
                          }
                      },
        get_cache_response = {
            'request_id': uuid(),
            'body': [
                cached_edge
            ],
            'status': 200,
        }

        link_metric_response = {
            'request_id': uuid(),
            'body': 'Failed',
            'status': 400,
        }

        enterprise_to_edge_info = {
            1: [cached_edge]
        }
        events_by_serial = {
            'VC1234567': [
                {
                    'event': 'LINK_DEAD',
                    'category': 'NETWORK',
                    'eventTime': '2019-07-30 07:38:00+00:00',
                    'message': 'GE2 dead'
                }
            ]
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_link_metrics = CoroutineMock(return_value=link_metric_response)

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(return_value=get_cache_response)

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        bouncing_detector._get_enterprise_to_cached_info_dict = Mock(return_value=enterprise_to_edge_info)
        bouncing_detector._get_events_by_serial_dict = CoroutineMock(return_value=events_by_serial)
        bouncing_detector._check_for_bouncing_events = CoroutineMock()

        await bouncing_detector._bouncing_detector_process()

        customer_cache_repository.get_cache_for_affecting_monitoring.assert_awaited_once()
        velocloud_repository.get_last_link_metrics.assert_awaited_once()

        bouncing_detector._get_enterprise_to_cached_info_dict.assert_not_called()
        bouncing_detector._get_events_by_serial_dict.assert_not_awaited()
        bouncing_detector._check_for_bouncing_events.assert_not_awaited()

    def get_enterprise_to_cached_info_dict_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1234}
        edge_full_id_2 = {"host": "metvco04.mettel.net", "enterprise_id": 1, "edge_id": 1235}
        edge_full_id_3 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': 'test-name',
            'serial_number': 'VC1234567',
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        cached_edge_2 = {
            'edge': edge_full_id_2,
            'edge_name': 'test-name',
            'serial_number': 'VC12345627',
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        cached_edge_3 = {
            'edge': edge_full_id_3,
            'edge_name': 'test-name',
            'serial_number': 'VC12345627',
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        expected_enterprise_to_edge_info = {
            1: [cached_edge_1, cached_edge_2],
            2: [cached_edge_3]
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)
        bouncing_detector._customer_cache = [cached_edge_1, cached_edge_2, cached_edge_3]

        enterprise_to_edge_info_dict = bouncing_detector._get_enterprise_to_cached_info_dict()
        assert enterprise_to_edge_info_dict == expected_enterprise_to_edge_info

    @pytest.mark.asyncio
    async def get_events_by_serial_dict_test(self):
        enterprise_id_1 = 1
        enterprise_id_2 = 2
        edge_name_1 = 'test'
        edge_name_2 = 'test_2'
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_1, "edge_id": 1234}
        edge_full_id_2 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_1, "edge_id": 1235}
        edge_full_id_3 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_2, "edge_id": 1234}

        edge_serial_1 = 'VC01'
        edge_serial_2 = 'VC012'
        edge_serial_3 = 'VC0123'

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_2,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        cached_edge_2 = {
            'edge': edge_full_id_2,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_2,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        cached_edge_3 = {
            'edge': edge_full_id_3,
            'edge_name': 'test-name-3',
            'serial_number': edge_serial_3,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        expected_enterprise_to_edge_info = {
            enterprise_id_1: [cached_edge_1, cached_edge_2],
            enterprise_id_2: [cached_edge_3]
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 dead',
            'edgeName': edge_name_1
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 dead',
            'edgeName': edge_name_2
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 dead',
            'edgeName': edge_name_1
        }
        event_4 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 dead',
            'edgeName': 'unknown name'
        }
        enterprise_event_response = {
            'request_id': uuid(),
            'body': [
                event_1, event_2, event_3, event_4
            ],
            'status': 200,
        }

        expected_events_by_serial = {
            edge_serial_2: [event_1, event_3],
            edge_serial_1: [event_2]
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_enterprise_events = CoroutineMock(return_value=enterprise_event_response)

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)
        bouncing_detector._customer_cache = [cached_edge_1, cached_edge_2, cached_edge_3]

        events_by_serial = await bouncing_detector._get_events_by_serial_dict(expected_enterprise_to_edge_info)

        velocloud_repository.get_last_enterprise_events.assert_has_awaits([call(enterprise_id_1),
                                                                           call(enterprise_id_2)])
        assert events_by_serial == expected_events_by_serial

    @pytest.mark.asyncio
    async def get_events_by_serial_dict_enterprise_events_return_non_2xx_test(self):
        enterprise_id_1 = 1
        enterprise_id_2 = 2
        edge_name_1 = 'test'
        edge_name_2 = 'test_2'
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_1, "edge_id": 1234}
        edge_full_id_2 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_1, "edge_id": 1235}
        edge_full_id_3 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_2, "edge_id": 1234}

        edge_serial_1 = 'VC01'
        edge_serial_2 = 'VC012'
        edge_serial_3 = 'VC0123'

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_2,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        cached_edge_2 = {
            'edge': edge_full_id_2,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_2,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        cached_edge_3 = {
            'edge': edge_full_id_3,
            'edge_name': 'test-name-3',
            'serial_number': edge_serial_3,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        expected_enterprise_to_edge_info = {
            enterprise_id_1: [cached_edge_1, cached_edge_2],
            enterprise_id_2: [cached_edge_3]
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 dead',
            'edgeName': edge_name_1
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 dead',
            'edgeName': edge_name_2
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 dead',
            'edgeName': edge_name_1
        }
        event_4 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'GE2 dead',
            'edgeName': 'unknown name'
        }
        enterprise_event_response = {
            'request_id': uuid(),
            'body': 'Failed',
            'status': 400,
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        velocloud_repository = Mock()
        velocloud_repository.get_last_enterprise_events = CoroutineMock(return_value=enterprise_event_response)

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)
        bouncing_detector._customer_cache = [cached_edge_1, cached_edge_2, cached_edge_3]

        events_by_serial = await bouncing_detector._get_events_by_serial_dict(expected_enterprise_to_edge_info)

        velocloud_repository.get_last_enterprise_events.assert_awaited_once_with(enterprise_id_1)
        assert events_by_serial == {}

    @pytest.mark.asyncio
    async def check_for_bouncing_events_test(self):
        ticket_id = 124
        enterprise_id_1 = 1
        edge_name_1 = 'test'
        edge_name_2 = 'test_2'
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_1, "edge_id": 1234}
        edge_full_id_2 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_1, "edge_id": 1235}

        edge_serial_1 = 'VC01'
        edge_serial_2 = 'VC012'

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_2,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        cached_edge_2 = {
            'edge': edge_full_id_2,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_2,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }

        event_1 = {
            'event': 'EDGE_DOWN',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Edge dead',
            'edgeName': edge_name_1
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE1 is now DEAD',
            'edgeName': edge_name_2
        }

        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD',
            'edgeName': edge_name_2
        }
        event_4 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE3 is now DEAD',
            'edgeName': edge_name_2
        }

        events_by_serial = {
            edge_serial_2: [event_1, event_1, event_1, event_1, event_1,
                            event_1, event_1, event_1, event_1, event_1, event_1],
            edge_serial_1: [event_2, event_2, event_2, event_2, event_2, event_2,
                            event_2, event_2, event_2, event_2, event_2, event_3,
                            event_4, event_4, event_4, event_4, event_4, event_4,
                            event_4, event_4, event_4, event_4, event_4]
        }

        edge_ticket_dict = {'test': 'name'}
        link_ticket_dict = {'test': 'name'}

        link_metric_1 = {"link": {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial_1,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        }
        link_metric_2 = {"link": {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial_1,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'GE2',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)
        bouncing_detector._customer_cache = [cached_edge_1, cached_edge_2]
        bouncing_detector._link_metrics_response = [link_metric_1, link_metric_2]
        bouncing_detector._get_edge_ticket_dict = Mock(return_value=edge_ticket_dict)
        bouncing_detector._get_link_ticket_dict = Mock(return_value=link_ticket_dict)
        bouncing_detector._create_bouncing_ticket = CoroutineMock(return_value=ticket_id)
        bouncing_detector._attempt_forward_to_asr = CoroutineMock()

        await bouncing_detector._check_for_bouncing_events(events_by_serial)

        bouncing_detector._get_edge_ticket_dict.assert_called_once_with(cached_edge_2, 11)
        bouncing_detector._get_link_ticket_dict.assert_called_once_with(cached_edge_1, link_metric_1["link"],
                                                                        "GE1", 11)
        bouncing_detector._create_bouncing_ticket.assert_has_awaits([call(cached_edge_2, edge_ticket_dict,
                                                                          edge_serial_2),
                                                                     call(cached_edge_1, link_ticket_dict,
                                                                          edge_serial_1)])
        bouncing_detector._attempt_forward_to_asr.assert_awaited_once_with(cached_edge_1, link_metric_1["link"],
                                                                           ticket_id)

    @pytest.mark.asyncio
    async def check_for_bouncing_events_none_ticket_id_return_test(self):
        ticket_id = None
        enterprise_id_1 = 1
        edge_name_1 = 'test'
        edge_name_2 = 'test_2'
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_1, "edge_id": 1234}
        edge_full_id_2 = {"host": "metvco04.mettel.net", "enterprise_id": enterprise_id_1, "edge_id": 1235}

        edge_serial_1 = 'VC01'
        edge_serial_2 = 'VC012'

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_2,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        cached_edge_2 = {
            'edge': edge_full_id_2,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_2,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }

        event_1 = {
            'event': 'EDGE_DOWN',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Edge dead',
            'edgeName': edge_name_1
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE1 is now DEAD',
            'edgeName': edge_name_2
        }

        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD',
            'edgeName': edge_name_2
        }
        event_4 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'Link GE3 is now DEAD',
            'edgeName': edge_name_2
        }

        events_by_serial = {
            edge_serial_2: [event_1, event_1, event_1, event_1, event_1,
                            event_1, event_1, event_1, event_1, event_1, event_1],
            edge_serial_1: [event_2, event_2, event_2, event_2, event_2, event_2,
                            event_2, event_2, event_2, event_2, event_2, event_3,
                            event_4, event_4, event_4, event_4, event_4, event_4,
                            event_4, event_4, event_4, event_4, event_4]
        }

        edge_ticket_dict = {'test': 'name'}
        link_ticket_dict = {'test': 'name'}

        link_metric_1 = {"link": {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial_1,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        }
        link_metric_2 = {"link": {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial_1,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'GE2',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)
        bouncing_detector._customer_cache = [cached_edge_1, cached_edge_2]
        bouncing_detector._link_metrics_response = [link_metric_1, link_metric_2]
        bouncing_detector._get_edge_ticket_dict = Mock(return_value=edge_ticket_dict)
        bouncing_detector._get_link_ticket_dict = Mock(return_value=link_ticket_dict)
        bouncing_detector._create_bouncing_ticket = CoroutineMock(return_value=ticket_id)
        bouncing_detector._attempt_forward_to_asr = CoroutineMock()

        await bouncing_detector._check_for_bouncing_events(events_by_serial)

        bouncing_detector._get_edge_ticket_dict.assert_called_once_with(cached_edge_2, 11)
        bouncing_detector._get_link_ticket_dict.assert_called_once_with(cached_edge_1, link_metric_1["link"],
                                                                        "GE1", 11)
        bouncing_detector._create_bouncing_ticket.assert_has_awaits([call(cached_edge_2, edge_ticket_dict,
                                                                          edge_serial_2),
                                                                     call(cached_edge_1, link_ticket_dict,
                                                                          edge_serial_1)])
        bouncing_detector._attempt_forward_to_asr.assert_not_awaited()

    def get_edge_ticket_dict_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': ['link_configuaration'],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        edge_ticket_dict = bouncing_detector._get_edge_ticket_dict(cached_edge_1, 11)
        assert isinstance(edge_ticket_dict, OrderedDict)

    def get_link_ticket_dict_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                                      'interfaces': ["GE1"],
                                      'mode': "PUBLIC",
                                      'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        link_metric_1 = {"link": {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial_1,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        link_ticket_dict = bouncing_detector._get_link_ticket_dict(cached_edge_1, link_metric_1["link"], 'GE1', 11)
        assert link_ticket_dict["Link Type"] == "Public Wired"
        assert isinstance(link_ticket_dict, OrderedDict)

    def get_link_ticket_dict_unknown_link_type_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                                      'interfaces': ["GE1"],
                                      'mode': "PUBLIC",
                                      'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': 12345,
                'client_name': 'Aperture Science',
            }
        }
        link_metric_1 = {"link": {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial_1,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        }
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        link_ticket_dict = bouncing_detector._get_link_ticket_dict(cached_edge_1, link_metric_1["link"], 'GE2', 11)
        assert link_ticket_dict["Link Type"] == "Unknown"
        assert isinstance(link_ticket_dict, OrderedDict)

    def ticket_object_to_string_test(self):
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_note = bouncing_detector._ticket_object_to_string(test_dict)
        assert ticket_note == "#*MetTel's IPA*#\nTrouble: Circuit Instability\n\nEdgeName: Test\nEdge Status: ok\n"

    def ticket_object_to_string_without_watermark_test(self):
        test_dict = {'EdgeName': 'Test', 'Edge Status': 'ok'}

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()
        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_note = bouncing_detector._ticket_object_to_string_without_watermark(test_dict)
        assert ticket_note == "\nTrouble: Circuit Instability\n\nEdgeName: Test\nEdge Status: ok\n"

    @pytest.mark.asyncio
    async def create_bouncing_ticket_ok_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                                      'interfaces': ["GE1"],
                                      'mode': "PUBLIC",
                                      'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        mock_device_by_id = [{
                                "serial": edge_serial_1,
                                "host": "mettel.velocloud.net",
                                "enterprise_id": 137,
                                "edge_id": 1651,
                                "contacts": {
                                    "ticket": {
                                        "email": "test@gmail.com",
                                        "phone": "123-456-4151",
                                        "name": "Man Test"
                                    },
                                    "site": {
                                        "email": "test@gmail.com",
                                        "phone": "123-456-4151",
                                        "name": "Man Test"
                                    }
                                }
                            }]
        ticket_id = 123
        mock_ticket_note = "some test ticket note"
        slack_message = f'Circuit Instability Ticket created with ticket id: {ticket_id}\n' \
                        f'https://app.bruin.com/helpdesk?clientId={client_id}&' \
                        f'ticketId={ticket_id} , in ' \
                        f'production'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["device_by_id"] = mock_device_by_id
        custom_monitor_config["environment"] = "production"
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_mock = {}
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value={'body': {'ticketIds': [ticket_id]},
                                                                               'status': 200})
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        bouncing_detector._attempt_forward_to_asr = CoroutineMock()

        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_1)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)
        bouncing_detector._attempt_forward_to_asr.assert_not_awaited()
        bruin_repository.get_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1)
        bruin_repository.create_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1,
                                                                          mock_device_by_id[0]["contacts"])
        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id=ticket_id, note=mock_ticket_note)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    @pytest.mark.asyncio
    async def create_bouncing_ticket_dev_environment_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                'interfaces': ["GE1"],
                'mode': "PUBLIC",
                'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        mock_device_by_id = [{
            "serial": edge_serial_1,
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "contacts": {
                "ticket": {
                    "email": "test@gmail.com",
                    "phone": "123-456-4151",
                    "name": "Man Test"
                },
                "site": {
                    "email": "test@gmail.com",
                    "phone": "123-456-4151",
                    "name": "Man Test"
                }
            }
        }]
        mock_ticket_note = "some test ticket note"

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["device_by_id"] = mock_device_by_id
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_mock = None
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value={'body': 'Failed',
                                                                               'status': 400})
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_1)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)
        bruin_repository.get_affecting_ticket.assert_not_awaited()
        bruin_repository.create_affecting_ticket.assert_not_awaited()
        bruin_repository.append_note_to_ticket.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def create_bouncing_ticket_none_affecting_tickets_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                'interfaces': ["GE1"],
                'mode': "PUBLIC",
                'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        mock_device_by_id = [{
            "serial": edge_serial_1,
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "contacts": {
                "ticket": {
                    "email": "test@gmail.com",
                    "phone": "123-456-4151",
                    "name": "Man Test"
                },
                "site": {
                    "email": "test@gmail.com",
                    "phone": "123-456-4151",
                    "name": "Man Test"
                }
            }
        }]
        mock_ticket_note = "some test ticket note"

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["device_by_id"] = mock_device_by_id
        custom_monitor_config["environment"] = "production"
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_mock = None
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value={'body': 'Failed',
                                                                               'status': 400})
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_1)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)
        bruin_repository.get_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1)
        bruin_repository.create_affecting_ticket.assert_not_awaited()
        bruin_repository.append_note_to_ticket.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def create_bouncing_ticket_ko_no_contact_info_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        edge_serial_2 = 'VC012'

        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                'interfaces': ["GE1"],
                'mode': "PUBLIC",
                'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        mock_device_by_id = [{
            "serial": edge_serial_1,
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "contacts": {
                "ticket": {
                    "email": "test@gmail.com",
                    "phone": "123-456-4151",
                    "name": "Man Test"
                },
                "site": {
                    "email": "test@gmail.com",
                    "phone": "123-456-4151",
                    "name": "Man Test"
                }
            }
        }]
        mock_ticket_note = "some test ticket note"

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["device_by_id"] = mock_device_by_id
        custom_monitor_config["environment"] = "production"
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_mock = {}
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock()
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_2)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)
        bruin_repository.get_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_2)
        bruin_repository.create_affecting_ticket.assert_not_awaited()
        bruin_repository.append_note_to_ticket.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def create_bouncing_ticket_ko_failed_affecting_rpc_request_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                'interfaces': ["GE1"],
                'mode': "PUBLIC",
                'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        mock_device_by_id = [{
            "serial": edge_serial_1,
            "host": "mettel.velocloud.net",
            "enterprise_id": 137,
            "edge_id": 1651,
            "contacts": {
                "ticket": {
                    "email": "test@gmail.com",
                    "phone": "123-456-4151",
                    "name": "Man Test"
                },
                "site": {
                    "email": "test@gmail.com",
                    "phone": "123-456-4151",
                    "name": "Man Test"
                }
            }
        }]
        mock_ticket_note = "some test ticket note"

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["device_by_id"] = mock_device_by_id
        custom_monitor_config["environment"] = "production"
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_mock = {}
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value={'body': 'Failed',
                                                                               'status': 400})
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_1)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)

        bruin_repository.get_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1)
        bruin_repository.create_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1,
                                                                          mock_device_by_id[0]["contacts"])
        bruin_repository.append_note_to_ticket.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def create_bouncing_ticket_ticket_exists_no_ticket_details_match_serial_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                'interfaces': ["GE1"],
                'mode': "PUBLIC",
                'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        ticket_id = 123
        mock_ticket_note = "some test ticket note"

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_mock = {
            "ticketID": ticket_id,
            "ticketDetails": [{"detailID": 5217537, "detailValue": edge_serial_1, "detailStatus": "O"}],
            "ticketNotes": []
        }
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value={'body': {'ticketIds': [ticket_id]},
                                                                               'status': 200})
        bruin_repository.find_detail_by_serial = Mock(return_value=None)
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_1)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)
        bruin_repository.get_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1)
        bruin_repository.find_detail_by_serial.assert_called_once_with(ticket_mock, edge_serial_1)
        bruin_repository.append_note_to_ticket.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def create_bouncing_ticket_unresolved_ticket_exists_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                'interfaces': ["GE1"],
                'mode': "PUBLIC",
                'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        ticket_id = 123
        mock_ticket_note = "some test ticket note"
        slack_message = f'Appending Circuit Instability note to unresolved ticket ' \
                        f'with ticket id: {ticket_id}\n' \
                        f'https://app.bruin.com/t/{ticket_id} , in production'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        ticket_mock = {
            "ticketID": ticket_id,
            "ticketDetails": [{"detailID": 5217537, "detailValue": edge_serial_1, "detailStatus": "O"}],
            "ticketNotes": []
        }
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value={'body': {'ticketIds': [ticket_id]},
                                                                               'status': 200})
        bruin_repository.find_detail_by_serial = Mock(return_value=ticket_mock["ticketDetails"][0])
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        bouncing_detector._attempt_forward_to_asr = CoroutineMock()
        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_1)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)
        bouncing_detector._attempt_forward_to_asr.assert_not_awaited()
        bruin_repository.get_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1)
        bruin_repository.find_detail_by_serial.assert_called_once_with(ticket_mock, edge_serial_1)
        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, mock_ticket_note)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    @pytest.mark.asyncio
    async def create_bouncing_ticket_resolved_ticket_exists_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                'interfaces': ["GE1"],
                'mode': "PUBLIC",
                'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        ticket_id = 123
        mock_ticket_note = "some test ticket note"
        mock_reopen_ticket_note = "some reopen ticket note"
        slack_message = f'Affecting ticket {ticket_id} reopened through bouncing-detector service. ' \
                        f'Details at https://app.bruin.com/t/{ticket_id}'

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        detail_id = 5217537
        ticket_mock = {
            "ticketID": ticket_id,
            "ticketDetails": [{"detailID": detail_id, "detailValue": edge_serial_1, "detailStatus": "R"}],
            "ticketNotes": []
        }
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value={'body': {'ticketIds': [ticket_id]},
                                                                               'status': 200})
        bruin_repository.find_detail_by_serial = Mock(return_value=ticket_mock["ticketDetails"][0])
        bruin_repository.open_ticket = CoroutineMock(return_value={'body': 'Success', 'status': 200})
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        bouncing_detector._ticket_object_to_string_without_watermark = Mock(return_value=mock_reopen_ticket_note)
        bouncing_detector._attempt_forward_to_asr = CoroutineMock()
        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_1)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)
        bouncing_detector._ticket_object_to_string_without_watermark.assert_called_once_with(ticket_dict)
        bouncing_detector._attempt_forward_to_asr.assert_not_awaited()
        bruin_repository.get_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1)
        bruin_repository.find_detail_by_serial.assert_called_once_with(ticket_mock, edge_serial_1)
        bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, detail_id)
        bruin_repository.append_reopening_note_to_ticket.assert_awaited_once_with(ticket_id, mock_reopen_ticket_note)
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    @pytest.mark.asyncio
    async def create_bouncing_ticket_resolved_ticket_exists_failed_reopen_rpc_test(self):
        edge_full_id_1 = {"host": "metvco04.mettel.net", "enterprise_id": 2, "edge_id": 1234}
        edge_name_1 = 'test'
        edge_serial_1 = 'VC01'
        client_id = 12345

        cached_edge_1 = {
            'edge': edge_full_id_1,
            'edge_name': edge_name_1,
            'serial_number': edge_serial_1,
            'last_contact': '2020-08-27T15:25:42.000',
            'logical_ids': ['logical_ids'],
            'links_configuration': [{
                'interfaces': ["GE1"],
                'mode': "PUBLIC",
                'type': "WIRED"}],
            'bruin_client_info': {
                'client_id': client_id,
                'client_name': 'Aperture Science',
            }
        }

        ticket_dict = {'ticket': 'some ticket details'}

        ticket_id = 123
        mock_ticket_note = "some test ticket note"
        mock_reopen_ticket_note = "some reopen ticket note"

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        bruin_repository = Mock()
        velocloud_repository = Mock()
        customer_cache_repository = Mock()
        notifications_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        detail_id = 5217537
        ticket_mock = {
            "ticketID": ticket_id,
            "ticketDetails": [{"detailID": detail_id, "detailValue": edge_serial_1, "detailStatus": "R"}],
            "ticketNotes": []
        }
        bruin_repository.get_affecting_ticket = CoroutineMock(return_value=ticket_mock)
        bruin_repository.append_note_to_ticket = CoroutineMock()
        bruin_repository.create_affecting_ticket = CoroutineMock(return_value={'body': {'ticketIds': [ticket_id]},
                                                                               'status': 200})
        bruin_repository.find_detail_by_serial = Mock(return_value=ticket_mock["ticketDetails"][0])
        bruin_repository.open_ticket = CoroutineMock(return_value={'body': 'Failure', 'status': 400})
        bruin_repository.append_reopening_note_to_ticket = CoroutineMock()
        bouncing_detector._ticket_object_to_string = Mock(return_value=mock_ticket_note)
        bouncing_detector._ticket_object_to_string_without_watermark = Mock(return_value=mock_reopen_ticket_note)
        notifications_repository.send_slack_message = CoroutineMock()

        with patch.dict(config.BOUNCING_DETECTOR_CONFIG, custom_monitor_config):
            await bouncing_detector._create_bouncing_ticket(cached_edge_1, ticket_dict, edge_serial_1)

        bouncing_detector._ticket_object_to_string.assert_called_once_with(ticket_dict)
        bouncing_detector._ticket_object_to_string_without_watermark.assert_not_called()
        bruin_repository.get_affecting_ticket.assert_awaited_once_with(client_id, edge_serial_1)
        bruin_repository.find_detail_by_serial.assert_called_once_with(ticket_mock, edge_serial_1)
        bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, detail_id)
        bruin_repository.append_reopening_note_to_ticket.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': 'Test Name',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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
        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial,
            "detailStatus": "I",
        }
        current_datetime = datetime.now()

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                edge_serial,
            ],
            "createdDate": current_datetime,
        }

        ticket_notes = [ticket_note_1]

        ticket_details_response = {
                                    'body': {
                                        'ticketDetails': [
                                            ticket_detail_1,
                                        ],
                                        'ticketNotes': ticket_notes,
                                    },
                                    'status': 200
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        slack_message = (
             f'Detail of Circuit Instability ticket {ticket_id} related to serial {edge_serial} '
             f'was successfully forwarded to {task_result} queue!'
        )

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.are_there_any_other_troubles.assert_called_once_with(ticket_notes)
        bruin_repository.change_detail_work_queue.assert_awaited_once_with(ticket_id, task_result,
                                                                           serial_number=edge_serial,
                                                                           detail_id=ticket_detail_1['detailID'])
        bruin_repository.append_asr_forwarding_note.assert_awaited_once_with(
            ticket_id, link_info, edge_serial
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_wireless_link_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': 'Test Name',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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
                        'type': 'WIRELESS',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }
        current_datetime = datetime.now()

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_not_awaited()
        bruin_repository.are_there_any_other_troubles.assert_not_called()
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_no_type_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': 'Test Name',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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
                        'interfaces': ['GE2'],
                        'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                        'mode': 'PUBLIC',
                        'type': 'WIRED',
                        'last_active': '2020-09-29T04:45:15.000Z'
                    }
                ]
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_not_awaited()
        bruin_repository.are_there_any_other_troubles.assert_not_called()
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_blacklisted_label_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': 'BYOB Test Name',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_not_awaited()
        bruin_repository.are_there_any_other_troubles.assert_not_called()
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_ip_label_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock()
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_not_awaited()
        bruin_repository.are_there_any_other_troubles.assert_not_called()
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_failed_ticket_details_rpc_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': 'Test Name',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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
        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial,
            "detailStatus": "I",
        }
        current_datetime = datetime.now()

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                edge_serial,
            ],
            "createdDate": current_datetime,
        }

        ticket_notes = [ticket_note_1]

        ticket_details_response = {
                                    'body': {},
                                    'status': 400
        }
        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        slack_message = (
             f'Detail of Circuit Instability ticket {ticket_id} related to serial {edge_serial} '
             f'was successfully forwarded to {task_result} queue!'
        )

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.are_there_any_other_troubles.assert_not_called()
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_failed_other_troubles_found_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': 'Test Name',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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
        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial,
            "detailStatus": "I",
        }
        current_datetime = datetime.now()

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                edge_serial,
            ],
            "createdDate": current_datetime,
        }

        ticket_notes = [ticket_note_1]

        ticket_details_response = {
                                    'body': {
                                        'ticketDetails': [
                                            ticket_detail_1,
                                        ],
                                        'ticketNotes': ticket_notes,
                                    },
                                    'status': 200
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=True)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.are_there_any_other_troubles.assert_called_once_with(ticket_notes)
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_already_forwarded_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': 'Test Name',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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
        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial,
            "detailStatus": "I",
        }

        current_datetime = datetime.now()
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
            "createdDate": current_datetime,
        }

        ticket_notes = [ticket_note_1, ticket_note_2]

        ticket_details_response = {
                                    'body': {
                                        'ticketDetails': [
                                            ticket_detail_1,
                                        ],
                                        'ticketNotes': ticket_notes,
                                    },
                                    'status': 200
        }

        change_detail_work_queue_response = {'body': "Success", 'status': 200}

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.are_there_any_other_troubles.assert_called_once_with(ticket_notes)
        bruin_repository.change_detail_work_queue.assert_not_awaited()
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def attempt_forward_to_asr_failed_work_queue_change_rpc_test(self):
        ticket_id = 12345
        edge_serial = 'VC5678901'
        task_result = 'No Trouble Found - Carrier Issue'

        link_info = {
            'host': 'some-host',
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
            'edgeSerialNumber': edge_serial,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': 'Test Name',
            'isp': None,
            'interface': 'GE1',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
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
        ticket_detail_1 = {
            "detailID": 2746937,
            "detailValue": edge_serial,
            "detailStatus": "I",
        }
        current_datetime = datetime.now()

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                edge_serial,
            ],
            "createdDate": current_datetime,
        }

        ticket_notes = [ticket_note_1]

        ticket_details_response = {
            'body': {
                'ticketDetails': [
                    ticket_detail_1,
                ],
                'ticketNotes': ticket_notes,
            },
            'status': 200
        }

        change_detail_work_queue_response = {'body': "Fail", 'status': 400}

        bruin_repository = Mock()
        bruin_repository.get_ticket_details = CoroutineMock(return_value=ticket_details_response)
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=change_detail_work_queue_response)
        bruin_repository.append_asr_forwarding_note = CoroutineMock()
        bruin_repository.are_there_any_other_troubles = Mock(return_value=False)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        custom_monitor_config = config.BOUNCING_DETECTOR_CONFIG.copy()
        custom_monitor_config["environment"] = "production"
        velocloud_repository = Mock()
        customer_cache_repository = Mock()

        bouncing_detector = BouncingDetector(event_bus, logger, scheduler, config, bruin_repository,
                                             velocloud_repository, customer_cache_repository, notifications_repository)

        await bouncing_detector._attempt_forward_to_asr(cached_edge, link_info, ticket_id)

        bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        bruin_repository.are_there_any_other_troubles.assert_called_once_with(ticket_notes)
        bruin_repository.change_detail_work_queue.assert_awaited_once_with(ticket_id, task_result,
                                                                           serial_number=edge_serial,
                                                                           detail_id=ticket_detail_1['detailID'])
        bruin_repository.append_asr_forwarding_note.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()
