from datetime import datetime
import json
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.actions import alert as alert_module
from application.actions.alert import Alert
from apscheduler.util import undefined
from asynctest import CoroutineMock

from config import testconfig


class TestAlert:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()

        alert = Alert(event_bus, scheduler, logger, config)

        assert alert._event_bus is event_bus
        assert alert._scheduler is scheduler
        assert alert._logger is logger
        assert alert._config is config

    @pytest.mark.asyncio
    async def start_alert_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = Mock()

        alert = Alert(event_bus, scheduler, logger, config)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(alert_module, 'datetime', new=datetime_mock):
            with patch.object(alert_module, 'timezone', new=Mock()):
                await alert.start_alert_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            alert._alert_process, 'cron',
            day=1, misfire_grace_time=86400,
            next_run_time=next_run_time,
            replace_existing=True,
            id='_alert_process',
        )

    @pytest.mark.asyncio
    async def start_alert_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = Mock()

        alert = Alert(event_bus, scheduler, logger, config)

        await alert.start_alert_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            alert._alert_process, 'cron',
            day=1, misfire_grace_time=86400,
            next_run_time=undefined,
            replace_existing=True,
            id='_alert_process',
        )

    @pytest.mark.asyncio
    async def alert_process_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        test_uuid = 'random-uuid'

        edge_1 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "123"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "2018-06-24T20:27:44.000Z",
                "modelNumber": "edge123"
            },
            "enterprise": "Fake Corp"
        }
        edge_2 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "456"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "2018-09-24T20:27:44.000Z",
                "modelNumber": "edge456"
            },
            "enterprise": "Fake Corp"
        }
        edge_3 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "789"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "2018-10-24T20:27:44.000Z",
                "modelNumber": "edge789"
            },
            "enterprise": "Fake Corp"
        }
        edges_list = [edge_1, edge_2, edge_3]
        event = {"request_id": 123, "edges": edges_list}
        email_contents = {'email': "<div>Some email</div>"}
        event_bus.rpc_request = CoroutineMock(return_value=event)

        alert = Alert(event_bus, scheduler, logger, config)
        alert._compose_email_object = Mock(return_value=email_contents)

        with patch.object(alert_module, 'uuid', return_value=test_uuid):
            await alert._alert_process()

        reported_edges = alert._compose_email_object.call_args[0][0]
        assert len(reported_edges) == 3
        alert._event_bus.rpc_request.assert_awaited_once_with(
            'alert.request.all.edges',
            json.dumps(dict(request_id=test_uuid, filter=[])),
            timeout=200
        )
        alert._event_bus.publish_message.assert_awaited_once_with(
            'notification.email.request',
            json.dumps(email_contents),
        )

    @pytest.mark.asyncio
    async def alert_process_with_invalid_last_contact_dates_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        test_uuid = 'random-uuid'

        edge_1 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "123"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "0000-00-00 00:00:00.000Z",
                "modelNumber": "edge123"
            },
            "enterprise": "Fake Corp"
        }
        edge_2 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "456"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "0000-00-00 00:00:00.000Z",
                "modelNumber": "edge456"
            },
            "enterprise": "Fake Corp"
        }
        edge_3 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "789"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "2018-10-24T20:27:44.000Z",
                "modelNumber": "edge789"
            },
            "enterprise": "Fake Corp"
        }
        event = {"request_id": 123, "edges": [edge_1, edge_2, edge_3]}
        email_contents = {'email': "<div>Some email</div>"}
        event_bus.rpc_request = CoroutineMock(return_value=event)

        alert = Alert(event_bus, scheduler, logger, config)
        alert._compose_email_object = Mock(return_value=email_contents)

        with patch.object(alert_module, 'uuid', return_value=test_uuid):
            await alert._alert_process()

        reported_edges = alert._compose_email_object.call_args[0][0]
        assert len(reported_edges) == 1
        alert._event_bus.rpc_request.assert_awaited_once_with(
            'alert.request.all.edges',
            json.dumps(dict(request_id=test_uuid, filter=[])),
            timeout=200
        )
        alert._event_bus.publish_message.assert_awaited_once_with(
            'notification.email.request',
            json.dumps(email_contents),
        )

    @pytest.mark.asyncio
    async def alert_process_with_less_than_30_days_elapsed_since_last_contact_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        test_uuid = 'random-uuid'

        edge_1 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "123"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "2018-06-20T20:27:44.000Z",
                "modelNumber": "edge123"
            },
            "enterprise": "Fake Corp"
        }
        edge_2 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "456"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "2018-06-25T20:27:44.000Z",
                "modelNumber": "edge456"
            },
            "enterprise": "Fake Corp"
        }
        edge_3 = {
            "edge_id": {
                "host": "some.host",
                "enterprise_id": "123",
                "edge_id": "789"
            },
            "edge": {
                "serialNumber": "some serial",
                "lastContact": "2018-06-30T20:27:44.000Z",
                "modelNumber": "edge789"
            },
            "enterprise": "Fake Corp"
        }
        edges_list = [edge_1, edge_2, edge_3]
        event = {"request_id": 123, "edges": edges_list}
        email_contents = {'email': "<div>Some email</div>"}
        event_bus.rpc_request = CoroutineMock(return_value=event)

        alert = Alert(event_bus, scheduler, logger, config)
        alert._compose_email_object = Mock(return_value=email_contents)

        current_timestamp = "2018-07-27T20:27:44.000Z"
        current_datetime = datetime.strptime(current_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        datetime_mock = Mock(wraps=datetime)
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(alert_module, 'datetime', new=datetime_mock):
            with patch.object(alert_module, 'uuid', return_value=test_uuid):
                await alert._alert_process()

        reported_edges = alert._compose_email_object.call_args[0][0]
        assert len(reported_edges) == 2
        alert._event_bus.rpc_request.assert_awaited_once_with(
            'alert.request.all.edges',
            json.dumps(dict(request_id=test_uuid, filter=[])),
            timeout=200
        )
        alert._event_bus.publish_message.assert_awaited_once_with(
            'notification.email.request',
            json.dumps(email_contents),
        )

    def compose_email_object_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG

        alert = Alert(event_bus, scheduler, logger, config)
        edges_to_report = [
            {"edge": {"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"},
             "enterprise": "Fake Corp"}]
        email = alert._compose_email_object(edges_to_report)
        assert 'Last contact edges' in email["email_data"]["subject"]
        assert config["last_contact"]["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
