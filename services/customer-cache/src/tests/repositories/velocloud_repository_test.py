from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories.utils_repository import to_json_bytes
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, "uuid", return_value=uuid_)


class TestVelocloudRepository:
    def instance_test(self):
        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(config, nats_client, notifications_repository)

        assert velocloud_repository._nats_client is nats_client
        assert velocloud_repository._config is config
        assert velocloud_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_edges_test(
        self, instance_velocloud_repository, instance_velocloud_request, instance_velocloud_response
    ):
        instance_velocloud_request["request_id"] = uuid_
        instance_velocloud_response["request_id"] = uuid_

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_velocloud_response)

        instance_velocloud_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await instance_velocloud_repository.get_edges_links_by_host("mettel.velocloud.net")

        instance_velocloud_repository._nats_client.request.assert_awaited_once_with(
            "get.links.with.edge.info", to_json_bytes(instance_velocloud_request), timeout=300
        )
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_failed_rpc_test(
        self, instance_velocloud_repository, instance_enterprise_velocloud_request
    ):
        instance_enterprise_velocloud_request["request_id"] = uuid_
        instance_velocloud_repository._nats_client.request = AsyncMock(side_effect=Exception)
        instance_velocloud_repository._notifications_repository.send_slack_message = AsyncMock()

        host = "mettel.velocloud.net"
        enterprise_id = "123"
        with uuid_mock:
            result = await instance_velocloud_repository._get_all_enterprise_edges(host, enterprise_id)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        instance_velocloud_repository._nats_client.request.assert_awaited_once_with(
            "request.enterprises.edges", to_json_bytes(instance_enterprise_velocloud_request), timeout=300
        )
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_non_2xx_test(
        self, instance_velocloud_repository, instance_enterprise_velocloud_request, instance_enterprise_edge_response
    ):
        instance_enterprise_velocloud_request["request_id"] = uuid_
        instance_enterprise_edge_response["request_id"] = uuid_
        instance_enterprise_edge_response["body"] = "Failed"
        instance_enterprise_edge_response["status"] = 400

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_enterprise_edge_response)

        instance_velocloud_repository._nats_client.request = AsyncMock(return_value=response_msg)
        instance_velocloud_repository._notifications_repository.send_slack_message = AsyncMock()

        host = "mettel.velocloud.net"
        enterprise_id = "123"
        with uuid_mock:
            result = await instance_velocloud_repository._get_all_enterprise_edges(host, enterprise_id)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        instance_velocloud_repository._nats_client.request.assert_awaited_once_with(
            "request.enterprises.edges", to_json_bytes(instance_enterprise_velocloud_request), timeout=300
        )
        assert result == instance_enterprise_edge_response

    @pytest.mark.asyncio
    async def get_all_velo_test(
        self, instance_velocloud_repository, instance_velocloud_response, instance_enterprise_edge_response
    ):
        wrong_request = {"body": [], "status": 400}
        host1 = testconfig.VELOCLOUD_HOST[0]
        host2 = testconfig.VELOCLOUD_HOST[1]
        host3 = testconfig.VELOCLOUD_HOST[2]
        host4 = testconfig.VELOCLOUD_HOST[3]

        response_msg_links = Mock(spec_set=Msg)
        response_msg_links.data = to_json_bytes(instance_velocloud_response)

        response_msg_wrong = Mock(spec_set=Msg)
        response_msg_wrong.data = to_json_bytes(wrong_request)

        response_msg_enterprise_edges = Mock(spec_set=Msg)
        response_msg_enterprise_edges.data = to_json_bytes(instance_enterprise_edge_response)

        instance_velocloud_repository._notifications_repository.send_slack_message = AsyncMock()
        instance_velocloud_repository._nats_client.request = AsyncMock(
            side_effect=[
                response_msg_links,
                response_msg_wrong,
                response_msg_wrong,
                response_msg_wrong,
                response_msg_enterprise_edges,
            ]
        )
        with uuid_mock:
            edges_with_serial = await instance_velocloud_repository.get_all_velo_edges()
        instance_velocloud_repository._nats_client.request.assert_has_awaits(
            [
                call(
                    "get.links.with.edge.info",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host1}}),
                    timeout=300,
                ),
                call(
                    "get.links.with.edge.info",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host2}}),
                    timeout=300,
                ),
                call(
                    "get.links.with.edge.info",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host3}}),
                    timeout=300,
                ),
                call(
                    "get.links.with.edge.info",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host4}}),
                    timeout=300,
                ),
                call(
                    "request.enterprises.edges",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host1, "enterprise_id": 1}}),
                    timeout=300,
                ),
            ]
        )
        assert len(edges_with_serial) == 2

    @pytest.mark.asyncio
    async def get_all_special_values_velo_test(
        self, instance_velocloud_repository, instance_special_velocloud_response, instance_enterprise_edge_response
    ):
        wrong_request = {"body": [], "status": 400}
        host1 = testconfig.VELOCLOUD_HOST[0]
        host2 = testconfig.VELOCLOUD_HOST[1]
        host3 = testconfig.VELOCLOUD_HOST[2]
        host4 = testconfig.VELOCLOUD_HOST[3]

        response_msg_links = Mock(spec_set=Msg)
        response_msg_links.data = to_json_bytes(instance_special_velocloud_response)

        response_msg_wrong = Mock(spec_set=Msg)
        response_msg_wrong.data = to_json_bytes(wrong_request)

        response_msg_enterprise_edges = Mock(spec_set=Msg)
        response_msg_enterprise_edges.data = to_json_bytes(instance_enterprise_edge_response)

        instance_velocloud_repository._notifications_repository.send_slack_message = AsyncMock()
        instance_velocloud_repository._nats_client.request = AsyncMock(
            side_effect=[
                response_msg_links,
                response_msg_wrong,
                response_msg_wrong,
                Exception,
                response_msg_enterprise_edges,
            ]
        )

        with uuid_mock:
            edges_with_serial = await instance_velocloud_repository.get_all_velo_edges()

        instance_velocloud_repository._nats_client.request.assert_has_awaits(
            [
                call(
                    "get.links.with.edge.info",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host1}}),
                    timeout=300,
                ),
                call(
                    "get.links.with.edge.info",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host2}}),
                    timeout=300,
                ),
                call(
                    "get.links.with.edge.info",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host3}}),
                    timeout=300,
                ),
                call(
                    "get.links.with.edge.info",
                    to_json_bytes({"request_id": uuid_, "body": {"host": host4}}),
                    timeout=300,
                ),
            ]
        )
        assert len(edges_with_serial) == 0

    @pytest.mark.asyncio
    async def get_edge_configuration_test(
        self, instance_velocloud_repository, instance_get_configuration_request, instance_config_response
    ):
        instance_get_configuration_request["request_id"] = uuid_

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_config_response)

        instance_velocloud_repository._nats_client.request = AsyncMock(return_value=response_msg)
        instance_velocloud_repository._notifications_repository.send_slack_message = AsyncMock()
        edge = {
            "host": instance_get_configuration_request["body"]["host"],
            "enterprise_id": instance_get_configuration_request["body"]["enterprise_id"],
            "edge_id": instance_get_configuration_request["body"]["edge_id"],
        }
        with uuid_mock:
            result = await instance_velocloud_repository.get_links_configuration(edge)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_not_awaited()
        instance_velocloud_repository._nats_client.request.assert_awaited_once_with(
            "request.links.configuration", to_json_bytes(instance_get_configuration_request), timeout=90
        )
        assert result == instance_config_response

    @pytest.mark.asyncio
    async def get_edge_configuration_with_response_having_non_2xx_status_test(
        self, instance_velocloud_repository, instance_get_configuration_request
    ):
        config_stack_response = {"status": 400, "body": []}
        instance_get_configuration_request["request_id"] = uuid_

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(config_stack_response)

        instance_velocloud_repository._nats_client.request = AsyncMock(return_value=response_msg)
        instance_velocloud_repository._notifications_repository.send_slack_message = AsyncMock()
        edge = {
            "host": instance_get_configuration_request["body"]["host"],
            "enterprise_id": instance_get_configuration_request["body"]["enterprise_id"],
            "edge_id": instance_get_configuration_request["body"]["edge_id"],
        }

        with uuid_mock:
            result = await instance_velocloud_repository.get_links_configuration(edge)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_awaited()
        instance_velocloud_repository._nats_client.request.assert_awaited_once_with(
            "request.links.configuration", to_json_bytes(instance_get_configuration_request), timeout=90
        )
        assert result["status"] == 400
        assert result["body"] == []

    @pytest.mark.asyncio
    async def get_edge_configuration_exception_test(
        self, instance_velocloud_repository, instance_get_configuration_request
    ):
        instance_get_configuration_request["request_id"] = uuid_
        instance_velocloud_repository._nats_client.request = AsyncMock(side_effect=Exception)
        instance_velocloud_repository._notifications_repository.send_slack_message = AsyncMock()
        edge = {
            "host": instance_get_configuration_request["body"]["host"],
            "enterprise_id": instance_get_configuration_request["body"]["enterprise_id"],
            "edge_id": instance_get_configuration_request["body"]["edge_id"],
        }

        with uuid_mock:
            result = await instance_velocloud_repository.get_links_configuration(edge)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_awaited()
        instance_velocloud_repository._nats_client.request.assert_awaited_once_with(
            "request.links.configuration", to_json_bytes(instance_get_configuration_request), timeout=90
        )
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def add_edge_config_test(self, instance_velocloud_repository, instance_config_response):
        instance_velocloud_repository.get_links_configuration = AsyncMock(return_value=instance_config_response)
        edge = {
            "edge": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 4,
                "edge_id": 12,
            }
        }
        result = await instance_velocloud_repository.add_edge_config(edge)
        assert len(result["links_configuration"]) == 2

    @pytest.mark.asyncio
    async def add_edge_config_bad_status_test(self, instance_velocloud_repository, instance_config_response):
        instance_config_response["status"] = 400
        instance_velocloud_repository.get_links_configuration = AsyncMock(return_value=instance_config_response)
        edge = {
            "edge": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 4,
                "edge_id": 12,
            }
        }
        result = await instance_velocloud_repository.add_edge_config(edge)
        assert len(result["links_configuration"]) == 0
