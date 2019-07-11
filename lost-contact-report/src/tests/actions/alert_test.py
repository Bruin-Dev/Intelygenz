import json
from unittest.mock import Mock

import pytest
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
        service_id = 123

        alert = Alert(event_bus, scheduler, logger, config, service_id)
        assert alert._event_bus is event_bus
        assert alert._scheduler is scheduler
        assert alert._logger is logger
        assert alert._config is config
        assert alert._service_id == service_id

    @pytest.mark.asyncio
    async def schedule_alert_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        config = Mock()
        service_id = 123

        alert = Alert(event_bus, scheduler, logger, config, service_id)
        await alert.start_alert_job(exec_on_start=False)
        assert 'cron' in scheduler.add_job.call_args[0][1]
        assert scheduler.add_job.call_args[1] == {'day': 1, 'misfire_grace_time': 86400, 'replace_existing': True,
                                                  'next_run_time': undefined, 'id': '_alert_process'}

    @pytest.mark.asyncio
    async def request_all_edges_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        alert = Alert(event_bus, scheduler, logger, config, service_id)
        await alert._request_all_edges()
        assert event_bus.publish_message.called
        assert "alert.request.all.edges" in event_bus.publish_message.call_args[0][0]

    @pytest.mark.asyncio
    async def receive_all_edges_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        service_id = 123

        alert = Alert(event_bus, scheduler, logger, config, service_id)
        alert._compose_email_object = Mock(return_value="<div>Some email</div>")
        event = json.dumps({"request_id": 123, "edges": [
            {"edge": {"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"},
             "enterprise": "Fake Corp"}]})
        await alert.receive_all_edges(event)
        assert event_bus.publish_message.called
        assert "notification.email.request" in event_bus.publish_message.call_args[0][0]
        assert "<div>Some email</div>" in event_bus.publish_message.call_args[0][1]

    def compose_email_test(self):
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig.ALERTS_CONFIG
        service_id = 123

        alert = Alert(event_bus, scheduler, logger, config, service_id)
        edges_to_report = [
            {"edge": {"serialNumber": "some serial", "lastContact": "2018-06-24T20:27:44.000Z"},
             "enterprise": "Fake Corp"}]
        email = alert._compose_email_object(edges_to_report)
        assert 'Lost contact edges' in email["email_data"]["subject"]
        assert config["lost_contact"]["recipient"] in email["email_data"]["recipient"]
        assert "<!DOCTYPE html" in email["email_data"]["html"]
