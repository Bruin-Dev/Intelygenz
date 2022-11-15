import json
from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from application.clients.bruin_client import BruinClient
from nats.aio.msg import Msg

EXAMPLE_SERIAL_NUMBER = "sn_test_1"
CLIENT_ID = 1
GET_CUSTOMER_INFO_RESPONSE = {"status": HTTPStatus.OK, "body": [{"client_id": 1234}]}
GET_CUSTOMER_INFO_RESPONSE_BAD_STATUS = {"status": HTTPStatus.BAD_REQUEST, "body": [{"client_id": 1234}]}
GET_MANAGEMENT_STATUS_RESPONSE = {"status": HTTPStatus.OK, "body": "test"}
GET_MANAGEMENT_STATUS_BAD_STATUS = {"status": HTTPStatus.BAD_REQUEST, "body": "test"}


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


NATS_AIO_MSG_BAD_STATUS = Msg(_client="NATS", data=to_json_bytes(GET_CUSTOMER_INFO_RESPONSE_BAD_STATUS))
NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(GET_CUSTOMER_INFO_RESPONSE))
NATS_AIO_MANAGEMENT_STATUS = Msg(_client="NATS", data=to_json_bytes(GET_MANAGEMENT_STATUS_RESPONSE))
NATS_AIO_MANAGEMENT_STATUS_BAD_STATUS = Msg(_client="NATS", data=to_json_bytes(GET_MANAGEMENT_STATUS_BAD_STATUS))


@pytest.fixture(scope="function")
def bruin_client_instance():
    return BruinClient(nats_client=Mock())


async def get_customer_info_from_serial_return_not_none_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
    customer_info = await bruin_client_instance.get_customer_info_from_serial(EXAMPLE_SERIAL_NUMBER)
    assert customer_info is not None


async def get_customer_info_from_serial_return_list_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
    customer_info = await bruin_client_instance.get_customer_info_from_serial(EXAMPLE_SERIAL_NUMBER)
    assert type(customer_info) is list


async def get_customer_info_from_serial_return_not_empty_list_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
    customer_info = await bruin_client_instance.get_customer_info_from_serial(EXAMPLE_SERIAL_NUMBER)
    assert len(customer_info) > 0


async def get_customer_info_from_serial_do_request_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
    await bruin_client_instance.get_customer_info_from_serial(EXAMPLE_SERIAL_NUMBER)
    bruin_client_instance.nats_client.request.assert_called()


async def get_customer_info_from_serial_return_empty_list_with_exception_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=Exception)
    customer_info = await bruin_client_instance.get_customer_info_from_serial(EXAMPLE_SERIAL_NUMBER)
    assert len(customer_info) == 0


async def get_customer_info_from_serial_return_empty_list_with_bad_status_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=NATS_AIO_MSG_BAD_STATUS)
    customer_info = await bruin_client_instance.get_customer_info_from_serial(EXAMPLE_SERIAL_NUMBER)
    assert len(customer_info) == 0


async def get_management_status_return_not_none_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=NATS_AIO_MANAGEMENT_STATUS)
    management_status = await bruin_client_instance.get_management_status(
        client_id=CLIENT_ID, serial_number=EXAMPLE_SERIAL_NUMBER
    )
    assert management_status is not None


async def get_management_status_return_str_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=NATS_AIO_MANAGEMENT_STATUS)
    management_status = await bruin_client_instance.get_management_status(
        client_id=CLIENT_ID, serial_number=EXAMPLE_SERIAL_NUMBER
    )
    assert type(management_status) is str


async def get_management_status_return_none_with_bad_status_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=NATS_AIO_MANAGEMENT_STATUS_BAD_STATUS)
    management_status = await bruin_client_instance.get_management_status(
        client_id=CLIENT_ID, serial_number=EXAMPLE_SERIAL_NUMBER
    )
    assert management_status is None


async def get_management_status_return_empty_list_with_exception_test(bruin_client_instance):
    bruin_client_instance.nats_client = AsyncMock()
    bruin_client_instance.nats_client.request = AsyncMock(return_value=Exception)
    management_status = await bruin_client_instance.get_management_status(
        client_id=CLIENT_ID, serial_number=EXAMPLE_SERIAL_NUMBER
    )
    assert management_status is None
