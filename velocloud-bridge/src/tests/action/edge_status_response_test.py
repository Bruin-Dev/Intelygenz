import json
from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock
from velocloud_client.client.velocloud_client import VelocloudClient

from application.actions.edge_status_response import ReportEdgeStatus
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig as config
from igz.packages.eventbus.eventbus import EventBus


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
        enterprise_info = "TEST"
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        velocloud_repo.get_edge_information().to_dict = Mock(return_value=dict(edge_status=[]))
        velocloud_repo.get_link_information = Mock(return_value=[])
        dict_object = Mock()
        dict_object.to_dict = Mock(return_value={"link_data": "STABLE", "linkId": "123"})
        velocloud_repo.get_link_information = Mock(return_value=[dict_object])
        velocloud_repo.get_link_service_groups_information = Mock(return_value=[])
        dict_service_object_wireless = Mock()
        dict_service_object_wireless.to_dict = Mock(return_value={"linkId": "321", "serviceGroups": "wireless"})
        dict_service_object_wired = Mock()
        dict_service_object_wired.to_dict = Mock(return_value={"linkId": "123", "serviceGroups": "wired"})
        velocloud_repo.get_link_service_groups_information = Mock(return_value=[dict_service_object_wireless,
                                                                                dict_service_object_wired])
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"}}
        await actions.report_edge_status(json.dumps(edge_msg).encode('utf-8'))
        assert velocloud_repo.get_enterprise_information.called
        assert velocloud_repo.get_enterprise_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_edge_information.called
        assert velocloud_repo.get_edge_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_link_information.called
        assert velocloud_repo.get_link_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_link_information.call_args[0][1] is None
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "edge_id": {"host": "host", "enterprise_id": "2",
                                                                                   "edge_id": "1"},
                                                                       "edge_info": {"enterprise_name": enterprise_info,
                                                                                     "edges": {"edge_status": []},
                                                                                     "links":
                                                                                         [{"link_data": "STABLE",
                                                                                           "linkId": "123",
                                                                                           "serviceGroups": "wired"}
                                                                                          ]},
                                                                       "status": 200})
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_status_ok_status_link_interval_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = "TEST"
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        velocloud_repo.get_edge_information().to_dict = Mock(return_value=dict(edge_status=[]))
        velocloud_repo.get_link_information = Mock(return_value=[])
        dict_object = Mock()
        dict_object.to_dict = Mock(return_value={"link_data": "STABLE", "linkId": "123"})
        velocloud_repo.get_link_information = Mock(return_value=[dict_object])
        velocloud_repo.get_link_service_groups_information = Mock(return_value=[])
        dict_service_object = Mock()
        dict_service_object.to_dict = Mock(return_value={"linkId": "123", "serviceGroups": "wireless"})
        velocloud_repo.get_link_service_groups_information = Mock(return_value=[dict_service_object])
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                    "interval": {"end": "now", "start": "15 mins ago"}}
        await actions.report_edge_status(json.dumps(edge_msg).encode('utf-8'))
        assert velocloud_repo.get_enterprise_information.called
        assert velocloud_repo.get_enterprise_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_edge_information.called
        assert velocloud_repo.get_edge_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_link_information.called
        assert velocloud_repo.get_link_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_link_information.call_args[0][1] == edge_msg["interval"]
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "edge_id": {"host": "host", "enterprise_id": "2",
                                                                                   "edge_id": "1"},
                                                                       "edge_info": {"enterprise_name": enterprise_info,
                                                                                     "edges": {"edge_status": []},
                                                                                     "links":
                                                                                         [{"link_data": "STABLE",
                                                                                           "linkId": "123",
                                                                                           "serviceGroups": "wireless"}
                                                                                          ]},
                                                                       "status": 200})
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_status_ko_no_service_group_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = "TEST"
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        velocloud_repo.get_edge_information().to_dict = Mock(return_value=dict(edge_status=[]))
        velocloud_repo.get_link_information = Mock(return_value=[])
        dict_object = Mock()
        dict_object.to_dict = Mock(return_value={"link_data": "STABLE", "linkId": "123"})
        velocloud_repo.get_link_information = Mock(return_value=[dict_object])
        velocloud_repo.get_link_service_groups_information = Mock(return_value=[])
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                    "interval": {"end": "now", "start": "15 mins ago"}}
        await actions.report_edge_status(json.dumps(edge_msg).encode('utf-8'))
        assert velocloud_repo.get_enterprise_information.called
        assert velocloud_repo.get_enterprise_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_edge_information.called
        assert velocloud_repo.get_edge_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_link_information.called
        assert velocloud_repo.get_link_information.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_link_information.call_args[0][1] == edge_msg["interval"]
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "edge_id": {"host": "host", "enterprise_id": "2",
                                                                                   "edge_id": "1"},
                                                                       "edge_info": {"enterprise_name": enterprise_info,
                                                                                     "edges": {"edge_status": []},
                                                                                     "links":
                                                                                         [{"link_data": "STABLE",
                                                                                           "linkId": "123"}
                                                                                          ]},
                                                                       "status": 200})
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_status_ko_empty_status_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = "TEST"
        edge_status = dict(edge_status=[])
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        velocloud_repo.get_edge_information().to_dict = Mock(return_value=edge_status)
        velocloud_repo.get_link_information = Mock(return_value=None)
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"}}
        await actions.report_edge_status(json.dumps(edge_msg).encode('utf-8'))
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "edge_id": {"host": "host", "enterprise_id": "2",
                                                                                   "edge_id": "1"},
                                                                       "edge_info": {"enterprise_name": enterprise_info,
                                                                                     "edges": edge_status,
                                                                                     "links": None},
                                                                       "status": 204})
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_status_ko_exception_status_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = "TEST"
        edge_status = dict(edge_status=[])
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        velocloud_repo.get_edge_information().to_dict = Mock(return_value=edge_status)
        velocloud_repo.get_link_information = Mock(return_value=Exception())
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"}}
        await actions.report_edge_status(json.dumps(edge_msg).encode('utf-8'))
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "edge_id": {"host": "host", "enterprise_id": "2",
                                                                                   "edge_id": "1"},
                                                                       "edge_info": {"enterprise_name": enterprise_info,
                                                                                     "edges": edge_status,
                                                                                     "links": ""},
                                                                       "status": 500})
        assert actions._logger.info.called
