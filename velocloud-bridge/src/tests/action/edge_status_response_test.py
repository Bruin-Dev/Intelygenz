import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from application.actions.edge_status_response import ReportEdgeStatus
from igz.packages.eventbus.eventbus import EventBus
from collections import namedtuple
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
from velocloud_client.client.velocloud_client import VelocloudClient
import json


class TestEdgeStatusResponse:

    def instance_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_velocloud_client = VelocloudClient(config)
        velocloud_repo = VelocloudRepository(config, mock_logger, test_velocloud_client)
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        assert actions._configs is config
        assert actions._logger is mock_logger
        assert test_bus._logger is mock_logger
        assert actions._event_bus is test_bus
        assert velocloud_repo._logger is mock_logger
        assert actions._velocloud_repository is velocloud_repo

    @pytest.mark.asyncio
    async def report_edge_status_ok_status_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = Mock()
        enterprise_info._name = Mock()
        edge_status = namedtuple("edge_status", [])
        edge_status._edgeState = 'CONNECTED'
        link_status = []
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        velocloud_repo.get_edge_information = Mock(return_value=edge_status)
        velocloud_repo.get_link_information = Mock(return_value=link_status)
        edge_msg = {"request_id": "123", "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"}}
        await actions.report_edge_status(json.dumps(edge_msg).encode('utf-8'))
        assert velocloud_repo.get_enterprise_information.called
        assert velocloud_repo.get_enterprise_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_edge_information.called
        assert velocloud_repo.get_edge_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_link_information.called
        assert velocloud_repo.get_link_information.call_args[0][0] == edge_msg["edge"]
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == 'edge.status.response'
        assert test_bus.publish_message.call_args[0][1] == repr({"request_id": "123",
                                                                 "edge_info": {"enterprise_name": enterprise_info,
                                                                               "edges": edge_status,
                                                                               "links": link_status},
                                                                 "status": 200})
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_status_ko_status_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = Mock()
        enterprise_info._name = Mock()
        edge_status = None
        link_status = 'OKAY'
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        velocloud_repo.get_edge_information = Mock(return_value=edge_status)
        velocloud_repo.get_link_information = Mock(return_value=link_status)
        edge_msg = {"request_id": "123", "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"}}
        await actions.report_edge_status(json.dumps(edge_msg).encode('utf-8'))
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == 'edge.status.response'
        assert test_bus.publish_message.call_args[0][1] == repr({"request_id": "123",
                                                                 "edge_info": {"enterprise_name": enterprise_info,
                                                                               "edges": edge_status,
                                                                               "links": link_status},
                                                                 "status": 500})
        assert actions._logger.info.called
