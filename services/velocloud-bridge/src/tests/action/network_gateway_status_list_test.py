from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from application.repositories.utils_repository import GenericResponse
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()
response_topic_ = "_INBOX.2007314fe0fcb2cdc2a2914c1"


class TestGatewayStatus:
    def instance_test(self, network_gateway_status_list_action, event_bus, logger, velocloud_repository):
        assert network_gateway_status_list_action._event_bus is event_bus
        assert network_gateway_status_list_action._logger is logger
        assert network_gateway_status_list_action._velocloud_repository is velocloud_repository

    @pytest.mark.asyncio
    async def get_network_gateway_status_list_test(
        self,
        make_rpc_request,
        make_network_gateway_status_body,
        network_gateway_status_list_action,
    ):
        velocloud_host = "mettel.velocloud.net"
        gateway_ids = [3, 4, 5]
        metrics = ["tunnelCount"]
        since = (datetime.now() - timedelta(minutes=5)).strftime("%m/%d/%Y, %H:%M:%S")
        request_body = {"host": velocloud_host, "metrics": metrics, "since": since}
        request = make_rpc_request(request_id=uuid_, response_topic=response_topic_, **request_body)
        response_status = HTTPStatus.OK
        response_body = make_network_gateway_status_body(gateway_ids=gateway_ids)
        repository_response = GenericResponse(body=response_body, status=response_status)
        response = {
            "request_id": uuid_,
            "body": repository_response.body,
            "status": repository_response.status,
        }
        network_gateway_status_list_action._velocloud_repository.get_network_gateway_status = CoroutineMock(
            return_value=repository_response
        )

        await network_gateway_status_list_action.get_network_gateway_status_list(request)

        velocloud_repo = network_gateway_status_list_action._velocloud_repository
        velocloud_repo.get_network_gateway_status.assert_awaited_once_with(velocloud_host, since, metrics)
        network_gateway_status_list_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic_, response
        )

    @pytest.mark.asyncio
    async def get_network_gateway_status_list_missing_mandatory_field_test(
        self,
        make_rpc_request,
        network_gateway_status_list_action,
    ):
        velocloud_host = "mettel.velocloud.net"
        request_body = {"host": velocloud_host}
        request = make_rpc_request(request_id=uuid_, response_topic=response_topic_, **request_body)

        await network_gateway_status_list_action.get_network_gateway_status_list(request)

        velocloud_repo = network_gateway_status_list_action._velocloud_repository
        velocloud_repo.get_network_gateway_status.assert_not_awaited()
        network_gateway_status_list_action._logger.warning.assert_called_with(
            f"Wrong request message: msg={request}, validation_error=2 validation errors for GatewayStatusMessageBody"
            f"\nsince\n  field required (type=value_error.missing)\nmetrics\n  "
            f"field required (type=value_error.missing)"
        )

    @pytest.mark.asyncio
    async def get_network_gateway_status_list_missing_body_test(
        self,
        make_rpc_request,
        network_gateway_status_list_action,
    ):
        request = make_rpc_request(request_id=uuid_, response_topic=response_topic_)

        await network_gateway_status_list_action.get_network_gateway_status_list(request)

        velocloud_repo = network_gateway_status_list_action._velocloud_repository
        velocloud_repo.get_network_gateway_status.assert_not_awaited()
        network_gateway_status_list_action._logger.warning.assert_called_with(
            f"Wrong request message: msg={request}, validation_error=1 validation error for GatewayStatusMessageBody"
            f"\n__root__\n  GatewayStatusMessageBody expected dict not NoneType (type=type_error)"
        )
