import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from application.actions.actions import Actions
from igz.packages.eventbus.eventbus import EventBus
import velocloud
from collections import namedtuple


class TestDroneActions:

    def instance_test(self):
        test_bus = EventBus()
        velocloud_repo = Mock()
        actions = Actions(test_bus, velocloud_repo)
        assert actions.event_bus is test_bus
        assert actions.velocloud_repository is velocloud_repo

    def process_edge_ok_test(self):
        test_bus = EventBus()
        velocloud_repo = Mock()
        velocloud_repo.get_edge_information = Mock(return_value="Edge is OK")
        actions = Actions(test_bus, velocloud_repo)
        edgeis = dict(host="somehost", enterpriseId=19, id=99)
        edge_status = actions._process_edge(edgeis)
        assert edge_status == "Edge is OK"
        assert velocloud_repo.get_edge_information.called

    def process_edge_ko_test(self):
        test_bus = EventBus()
        velocloud_repo = Mock()
        velocloud_repo.get_edge_information = Mock(side_effect=velocloud.rest.ApiException())
        actions = Actions(test_bus, velocloud_repo)
        edgeis = dict(host="somehost", enterpriseId=19, id=99)
        edge_status = actions._process_edge(edgeis)
        assert edge_status is None
        assert velocloud_repo.get_edge_information.called

    @pytest.mark.asyncio
    async def report_edge_status_ko_status_test(self):
        test_bus = EventBus()
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = Actions(test_bus, velocloud_repo)
        edge_status = namedtuple("edge_status", [])
        edge_status._edgeState = 'FAILING'
        actions._process_edge = Mock(return_value=edge_status)
        await actions.report_edge_status(b'{"SomeIds": "ids"}')
        assert test_bus.publish_message.called
        assert actions._process_edge.called
        assert actions._process_edge.call_args[0][0] == dict(SomeIds="ids")
        assert test_bus.publish_message.call_args[0][0] == 'edge.status.ko'

    @pytest.mark.asyncio
    async def report_edge_status_ok_status_test(self):
        test_bus = EventBus()
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = Actions(test_bus, velocloud_repo)
        edge_status = namedtuple("edge_status", [])
        edge_status._edgeState = 'CONNECTED'
        actions._process_edge = Mock(return_value=edge_status)
        await actions.report_edge_status(b'{"SomeIds": "ids"}')
        assert test_bus.publish_message.called
        assert actions._process_edge.called
        assert actions._process_edge.call_args[0][0] == dict(SomeIds="ids")
        assert test_bus.publish_message.call_args[0][0] == 'edge.status.ok'
