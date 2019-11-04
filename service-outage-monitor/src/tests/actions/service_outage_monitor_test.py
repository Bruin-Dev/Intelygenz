from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import json
from datetime import datetime
from datetime import timedelta
from shortuuid import uuid

import pytest
from application.actions import service_outage_monitor as service_outage_monitor_module
from application.actions.service_outage_monitor import ServiceOutageMonitor
from apscheduler.util import undefined
from asynctest import CoroutineMock

from config import testconfig
from application.repositories.template_management import TemplateRenderer


class TestServiceOutageMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        template_renderer = Mock()

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler,
                                                      config, template_renderer)

        assert service_outage_monitor._event_bus is event_bus
        assert service_outage_monitor._logger is logger
        assert service_outage_monitor._scheduler is scheduler
        assert service_outage_monitor._config is config

    @pytest.mark.asyncio
    async def start_service_outage_monitor_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        template_renderer = Mock()

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(service_outage_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(service_outage_monitor_module, 'timezone', new=Mock()):
                await service_outage_monitor.start_service_outage_monitor_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            service_outage_monitor._service_outage_monitor_process, 'interval',
            seconds=900,
            next_run_time=next_run_time,
            replace_existing=True,
            id='_service_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_service_outage_monitor_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        template_renderer = Mock()

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)

        await service_outage_monitor.start_service_outage_monitor_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            service_outage_monitor._service_outage_monitor_process, 'interval',
            seconds=900,
            next_run_time=undefined,
            replace_existing=True,
            id='_service_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def service_outage_monitor_process_test(self):
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        edge_list = {'edges': []}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)

        uuid_ = uuid()
        with patch.object(service_outage_monitor_module, 'uuid', return_value=uuid_):
            await service_outage_monitor._service_outage_monitor_process()

        event_bus.rpc_request.assert_awaited_once_with(
            'edge.list.request',
            json.dumps({
                'request_id': uuid_,
                'filter': [
                    {'host': 'mettel.velocloud.net', 'enterprise_ids': []},
                    {'host': 'metvco03.mettel.net', 'enterprise_ids': []},
                    {'host': 'metvco04.mettel.net', 'enterprise_ids': []},
                ]
            }),
            timeout=60,
        )

    @pytest.mark.asyncio
    async def service_outage_monitor_process_with_connected_edges_test(self):
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        edge_list = {'edges': ['edge-1', 'edge-2', 'edge-3']}

        edge_1_status = {
            'edge_id': 'edge-1',
            'edge_info': {'edges': {'edgeState': 'CONNECTED'}}
        }
        edge_2_status = {
            'edge_id': 'edge-2',
            'edge_info': {'edges': {'edgeState': 'CONNECTED'}}
        }
        edge_3_status = {
            'edge_id': 'edge-3',
            'edge_info': {'edges': {'edgeState': 'CONNECTED'}}
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_list,
            edge_1_status,
            edge_2_status,
            edge_3_status,
        ])

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_outage_monitor._template_renderer._compose_email_object = Mock()

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        uuid_4 = uuid()

        with patch.object(service_outage_monitor_module, 'uuid', side_effect=[uuid_1, uuid_2, uuid_3, uuid_4]):
            await service_outage_monitor._service_outage_monitor_process()

        event_bus.rpc_request.assert_has_awaits([
            call(
                'edge.list.request',
                json.dumps({
                    'request_id': uuid_1,
                    'filter': [
                        {'host': 'mettel.velocloud.net', 'enterprise_ids': []},
                        {'host': 'metvco03.mettel.net', 'enterprise_ids': []},
                        {'host': 'metvco04.mettel.net', 'enterprise_ids': []},
                    ]
                }),
                timeout=60,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_2,
                    'edge': 'edge-1',
                }),
                timeout=45,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_3,
                    'edge': 'edge-2',
                }),
                timeout=45,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_4,
                    'edge': 'edge-3',
                }),
                timeout=45,
            ),
        ], any_order=True)
        service_outage_monitor._template_renderer._compose_email_object.assert_not_called()

    @pytest.mark.asyncio
    async def service_outage_monitor_process_with_offline_edges_test(self):
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        edge_list = {'edges': ['edge-1', 'edge-2', 'edge-3']}

        edge_1_status = {
            'edge_id': 'edge-1',
            'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
        }
        edge_2_status = {
            'edge_id': 'edge-2',
            'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
        }
        edge_3_status = {
            'edge_id': 'edge-3',
            'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
        }

        edge_1_events = {'edge_1_events': ['Some event info']}
        edge_2_events = {'edge_2_events': ['Some event info']}
        edge_3_events = {'edge_3_events': ['Some event info']}

        edge_1_email = {'edge_1_email': 'Failure'}
        edge_2_email = {'edge_2_email': 'Success'}
        edge_3_email = {'edge_3_email': 'Failure'}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_list,
            edge_1_status, edge_1_events, edge_1_email,
            edge_2_status, edge_2_events, edge_2_email,
            edge_3_status, edge_3_events, edge_3_email,
        ])

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_outage_monitor._template_renderer._compose_email_object = Mock(side_effect=[
            edge_1_email, edge_2_email, edge_3_email,
        ])

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        uuid_4 = uuid()
        uuid_5 = uuid()
        uuid_6 = uuid()
        uuid_7 = uuid()
        uuid_side_effect = [
            uuid_1, uuid_2, uuid_3, uuid_4, uuid_5, uuid_6, uuid_7,
        ]

        current_datetime = datetime.now()
        current_datetime_previous_week = current_datetime - timedelta(days=7)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(service_outage_monitor_module, 'uuid', side_effect=uuid_side_effect):
            with patch.object(service_outage_monitor_module, 'datetime', new=datetime_mock):
                await service_outage_monitor._service_outage_monitor_process()

        event_bus.rpc_request.assert_has_awaits([
            call(
                'edge.list.request',
                json.dumps({
                    'request_id': uuid_1,
                    'filter': [
                        {'host': 'mettel.velocloud.net', 'enterprise_ids': []},
                        {'host': 'metvco03.mettel.net', 'enterprise_ids': []},
                        {'host': 'metvco04.mettel.net', 'enterprise_ids': []},
                    ]
                }),
                timeout=60,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_2,
                    'edge': 'edge-1',
                }),
                timeout=45,
            ),
            call(
                f'alert.request.event.edge',
                json.dumps({
                    'request_id': uuid_3,
                    'edge': 'edge-1',
                    'start_date': current_datetime_previous_week,
                    'end_date': current_datetime,
                }, default=str),
                timeout=10,
            ),
            call(
                'notification.email.request',
                json.dumps(edge_1_email),
                timeout=10,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_4,
                    'edge': 'edge-2',
                }),
                timeout=45,
            ),
            call(
                f'alert.request.event.edge',
                json.dumps({
                    'request_id': uuid_5,
                    'edge': 'edge-2',
                    'start_date': current_datetime_previous_week,
                    'end_date': current_datetime,
                }, default=str),
                timeout=10,
            ),
            call(
                'notification.email.request',
                json.dumps(edge_2_email),
                timeout=10,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_6,
                    'edge': 'edge-3',
                }),
                timeout=45,
            ),
            call(
                f'alert.request.event.edge',
                json.dumps({
                    'request_id': uuid_7,
                    'edge': 'edge-3',
                    'start_date': current_datetime_previous_week,
                    'end_date': current_datetime,
                }, default=str),
                timeout=10,
            ),
            call(
                'notification.email.request',
                json.dumps(edge_3_email),
                timeout=10,
            ),
        ], any_order=False)
        assert service_outage_monitor._template_renderer._compose_email_object.call_count == 3

    @pytest.mark.asyncio
    async def service_outage_monitor_process_with_unknown_edge_state_test(self):
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()
        config = testconfig
        template_renderer = Mock()
        edge_list = {'edges': ['edge-1', 'edge-2', 'edge-3']}

        edge_1_status = {
            'edge_id': 'edge-1',
            'edge_info': {'edges': {'edgeState': 'UNKNOWN'}}
        }
        edge_2_status = {
            'edge_id': 'edge-2',
            'edge_info': {'edges': {'edgeState': 'UNKNOWN'}}
        }
        edge_3_status = {
            'edge_id': 'edge-3',
            'edge_info': {'edges': {'edgeState': 'UNKNOWN'}}
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_list,
            edge_1_status,
            edge_2_status,
            edge_3_status,
        ])

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_outage_monitor._template_renderer._compose_email_object = Mock()

        uuid_1 = uuid()
        uuid_2 = uuid()
        uuid_3 = uuid()
        uuid_4 = uuid()

        with patch.object(service_outage_monitor_module, 'uuid', side_effect=[uuid_1, uuid_2, uuid_3, uuid_4]):
            await service_outage_monitor._service_outage_monitor_process()

        event_bus.rpc_request.assert_has_awaits([
            call(
                'edge.list.request',
                json.dumps({
                    'request_id': uuid_1,
                    'filter': [
                        {'host': 'mettel.velocloud.net', 'enterprise_ids': []},
                        {'host': 'metvco03.mettel.net', 'enterprise_ids': []},
                        {'host': 'metvco04.mettel.net', 'enterprise_ids': []},
                    ]
                }),
                timeout=60,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_2,
                    'edge': 'edge-1',
                }),
                timeout=45,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_3,
                    'edge': 'edge-2',
                }),
                timeout=45,
            ),
            call(
                'edge.status.request',
                json.dumps({
                    'request_id': uuid_4,
                    'edge': 'edge-3',
                }),
                timeout=45,
            ),
        ], any_order=True)
        service_outage_monitor._template_renderer._compose_email_object.assert_not_called()

    @pytest.mark.asyncio
    async def service_outage_monitor_process_with_dev_environment_test(self):
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()

        edge_list = {'edges': ['edge-1']}

        edge_status = {
            'edge_id': 'edge-1',
            'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
        }
        edge_events = {'edge_events': ['Some event info']}
        edge_email = {'edge_email': 'Failure'}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_list,
            edge_status, edge_events, edge_email,
        ])

        config = Mock()
        template_renderer = Mock()

        config.MONITOR_CONFIG = {'environment': 'dev'}

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler,
                                                      config, template_renderer)
        service_outage_monitor._template_renderer._compose_email_object = Mock(return_value=edge_email)

        await service_outage_monitor._service_outage_monitor_process()

        service_outage_monitor._template_renderer._compose_email_object.assert_called()

    @pytest.mark.asyncio
    async def service_outage_monitor_process_with_production_environment_test(self):
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()

        edge_list = {'edges': ['edge-1']}

        edge_status = {
            'edge_id': 'edge-1',
            'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
        }
        edge_events = {'edge_events': ['Some event info']}
        edge_email = {'edge_email': 'Failure'}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[
            edge_list,
            edge_status, edge_events, edge_email,
        ])

        config = Mock()
        template_renderer = Mock()
        config.MONITOR_CONFIG = {'environment': 'production'}

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_outage_monitor._template_renderer._compose_email_object = Mock(return_value=edge_email)

        await service_outage_monitor._service_outage_monitor_process()

        service_outage_monitor._template_renderer._compose_email_object.assert_called()

    @pytest.mark.asyncio
    async def service_outage_monitor_process_with_unknown_config_test(self):
        logger = Mock()
        logger.error = Mock()
        scheduler = Mock()

        edge_list = {'edges': ['edge-1']}
        edge_status = {
            'edge_id': 'edge-1',
            'edge_info': {'edges': {'edgeState': 'OFFLINE'}}
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=[edge_list, edge_status])

        config = Mock()
        template_renderer = Mock()
        config.MONITOR_CONFIG = {'environment': None}

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)
        service_outage_monitor._template_renderer._compose_email_object = Mock()

        await service_outage_monitor._service_outage_monitor_process()

        service_outage_monitor._template_renderer._compose_email_object.assert_not_called()

    def find_recent_occurence_of_event_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        template_renderer = Mock()

        edge_alive_state = "EDGE_ALIVE"
        link_alive_state = "LINK_ALIVE"

        edge_back_message = 'Edge is back up'
        link_ge2_message = 'Link GE2 is no longer DEAD'

        event_list = [
            {
                'event': edge_alive_state,
                'eventTime': '2019-07-30 06:38:00+00:00',
                'message': edge_back_message
            },
            {
                'event': link_alive_state,
                'eventTime': '2019-07-30 4:26:00+00:00',
                'message': link_ge2_message
            },
            {
                'event': edge_alive_state,
                'eventTime': '2019-07-29 06:38:00+00:00',
                'message': edge_back_message
            }
        ]

        service_outage_monitor = ServiceOutageMonitor(event_bus, logger, scheduler, config, template_renderer)

        edge_online_time = service_outage_monitor._find_recent_occurence_of_event(
            event_list, event_type=edge_alive_state, message=None)
        assert edge_online_time == '2019-07-30 06:38:00+00:00'

        link_online_time = service_outage_monitor._find_recent_occurence_of_event(
            event_list, event_type=link_alive_state, message=link_ge2_message)
        assert link_online_time == '2019-07-30 4:26:00+00:00'

        link_dead_time = service_outage_monitor._find_recent_occurence_of_event(
            event_list, event_type=link_alive_state, message='Missing message')
        assert link_dead_time is None
