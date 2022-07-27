from unittest.mock import Mock, call, patch

import pytest
from application.repositories import nats_error_response
from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories.velocloud_repository import VelocloudRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, "uuid", return_value=uuid_)


class TestVelocloudRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(config, logger, event_bus, notifications_repository)

        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is config
        assert velocloud_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_edges_with_default_rpc_timeout_test(
        self, instance_velocloud_repository, instance_velocloud_request, instance_velocloud_response
    ):
        instance_velocloud_request["request_id"] = uuid_
        instance_velocloud_response["request_id"] = uuid_
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        with uuid_mock:
            result = await instance_velocloud_repository.get_edges_links_by_host("mettel.velocloud.net")

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.with.edge.info", instance_velocloud_request, timeout=300
        )
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_edges_with_custom_rpc_timeout_test(
        self, instance_velocloud_repository, instance_velocloud_request, instance_velocloud_response
    ):
        instance_velocloud_request["request_id"] = uuid_
        instance_velocloud_response["request_id"] = uuid_
        rpc_timeout = 1000
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        with uuid_mock:
            result = await instance_velocloud_repository.get_edges_links_by_host(
                "mettel.velocloud.net", rpc_timeout=rpc_timeout
            )

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.with.edge.info", instance_velocloud_request, timeout=rpc_timeout
        )
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_all_enterprise_edges_failed_rpc_test(
        self, instance_velocloud_repository, instance_enterprise_velocloud_request
    ):
        instance_enterprise_velocloud_request["request_id"] = uuid_
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        instance_velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()

        host = "mettel.velocloud.net"
        enterprise_id = "123"
        with uuid_mock:
            result = await instance_velocloud_repository._get_all_enterprise_edges(host, enterprise_id)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.enterprises.edges", instance_enterprise_velocloud_request, timeout=300
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

        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(
            return_value=instance_enterprise_edge_response
        )
        instance_velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()

        host = "mettel.velocloud.net"
        enterprise_id = "123"
        with uuid_mock:
            result = await instance_velocloud_repository._get_all_enterprise_edges(host, enterprise_id)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.enterprises.edges", instance_enterprise_velocloud_request, timeout=300
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
        instance_velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[
                instance_velocloud_response,
                wrong_request,
                wrong_request,
                wrong_request,
                instance_enterprise_edge_response,
            ]
        )
        with uuid_mock:
            edges_with_serial = await instance_velocloud_repository.get_all_velo_edges()
        instance_velocloud_repository._event_bus.rpc_request.assert_has_awaits(
            [
                call("get.links.with.edge.info", {"request_id": uuid_, "body": {"host": host1}}, timeout=300),
                call("get.links.with.edge.info", {"request_id": uuid_, "body": {"host": host2}}, timeout=300),
                call("get.links.with.edge.info", {"request_id": uuid_, "body": {"host": host3}}, timeout=300),
                call("get.links.with.edge.info", {"request_id": uuid_, "body": {"host": host4}}, timeout=300),
                call(
                    "request.enterprises.edges",
                    {"request_id": uuid_, "body": {"host": host1, "enterprise_id": 1}},
                    timeout=90,
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
        instance_velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[
                instance_special_velocloud_response,
                wrong_request,
                wrong_request,
                Exception,
                instance_enterprise_edge_response,
            ]
        )
        with uuid_mock:
            edges_with_serial = await instance_velocloud_repository.get_all_velo_edges()
        instance_velocloud_repository._event_bus.rpc_request.assert_has_awaits(
            [
                call("get.links.with.edge.info", {"request_id": uuid_, "body": {"host": host1}}, timeout=300),
                call("get.links.with.edge.info", {"request_id": uuid_, "body": {"host": host2}}, timeout=300),
                call("get.links.with.edge.info", {"request_id": uuid_, "body": {"host": host3}}, timeout=300),
                call("get.links.with.edge.info", {"request_id": uuid_, "body": {"host": host4}}, timeout=300),
            ]
        )
        assert len(edges_with_serial) == 0

    @pytest.mark.asyncio
    async def get_edge_configuration_test(
        self, instance_velocloud_repository, instance_get_configuration_request, instance_config_response
    ):
        instance_get_configuration_request["request_id"] = uuid_
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_config_response)
        instance_velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        edge = {
            "host": instance_get_configuration_request["body"]["host"],
            "enterprise_id": instance_get_configuration_request["body"]["enterprise_id"],
            "edge_id": instance_get_configuration_request["body"]["edge_id"],
        }
        with uuid_mock:
            result = await instance_velocloud_repository.get_links_configuration(edge)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_not_awaited()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.links.configuration", instance_get_configuration_request, timeout=30
        )
        assert result == instance_config_response

    @pytest.mark.asyncio
    async def get_edge_configuration_with_response_having_non_2xx_status_test(
        self, instance_velocloud_repository, instance_get_configuration_request
    ):
        config_stack_response = {"status": 400, "body": []}
        instance_get_configuration_request["request_id"] = uuid_
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=config_stack_response)
        instance_velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        edge = {
            "host": instance_get_configuration_request["body"]["host"],
            "enterprise_id": instance_get_configuration_request["body"]["enterprise_id"],
            "edge_id": instance_get_configuration_request["body"]["edge_id"],
        }

        with uuid_mock:
            result = await instance_velocloud_repository.get_links_configuration(edge)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_awaited()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.links.configuration", instance_get_configuration_request, timeout=30
        )
        assert result["status"] == 400
        assert result["body"] == []

    @pytest.mark.asyncio
    async def get_edge_configuration_exception_test(
        self, instance_velocloud_repository, instance_get_configuration_request
    ):
        instance_get_configuration_request["request_id"] = uuid_
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        instance_velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()
        edge = {
            "host": instance_get_configuration_request["body"]["host"],
            "enterprise_id": instance_get_configuration_request["body"]["enterprise_id"],
            "edge_id": instance_get_configuration_request["body"]["edge_id"],
        }

        with uuid_mock:
            result = await instance_velocloud_repository.get_links_configuration(edge)

        instance_velocloud_repository._notifications_repository.send_slack_message.assert_awaited()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.links.configuration", instance_get_configuration_request, timeout=30
        )
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def add_edge_config_test(self, instance_velocloud_repository, instance_config_response):
        instance_velocloud_repository.get_links_configuration = CoroutineMock(return_value=instance_config_response)
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
        instance_velocloud_repository.get_links_configuration = CoroutineMock(return_value=instance_config_response)
        edge = {
            "edge": {
                "host": "mettel.velocloud.net",
                "enterprise_id": 4,
                "edge_id": 12,
            }
        }
        result = await instance_velocloud_repository.add_edge_config(edge)
        assert len(result["links_configuration"]) == 0
