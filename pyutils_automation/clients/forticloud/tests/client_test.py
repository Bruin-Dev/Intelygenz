from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from forticloud_client.exceptions.login_error import LoginError


async def create_session_return_none_test(forticloud_client):
    result = await forticloud_client.create_session()
    assert result is None


async def create_session_create_session_value_test(forticloud_client):
    await forticloud_client.create_session()
    assert forticloud_client.session is not None


async def create_session_create_session_value_is_aiohttp_type_test(forticloud_client):
    await forticloud_client.create_session()
    assert type(forticloud_client.session) == aiohttp.ClientSession


async def close_session_return_none_test(forticloud_client):
    await forticloud_client.create_session()
    result = await forticloud_client.close_session()
    assert result is None


async def close_session_not_delete_session_value_test(forticloud_client):
    await forticloud_client.create_session()
    await forticloud_client.close_session()
    assert forticloud_client.session is not None


async def close_session_value_is_aiohttp_type_test(forticloud_client):
    await forticloud_client.create_session()
    await forticloud_client.close_session()
    assert type(forticloud_client.session) == aiohttp.ClientSession


def get_request_headers_not_return_none_test(forticloud_client):
    headers = forticloud_client.get_request_headers()
    assert headers is not None


def get_request_headers_return_a_dict_test(forticloud_client):
    headers = forticloud_client.get_request_headers()
    assert type(headers) == dict


def get_request_headers_return_content_type_test(forticloud_client):
    headers = forticloud_client.get_request_headers()
    assert "Content-Type" in headers


def get_request_headers_return_authorization_test(forticloud_client):
    headers = forticloud_client.get_request_headers()
    assert "Authorization" in headers


def get_if_need_to_do_login_return_not_none_test(forticloud_client):
    need_login = forticloud_client.get_if_need_to_do_login()
    assert need_login is not None


def get_if_need_to_do_login_return_bool_test(forticloud_client):
    need_login = forticloud_client.get_if_need_to_do_login()
    assert type(need_login) == bool


def get_if_need_to_do_login_return_true_if_not_token_test(forticloud_client):
    forticloud_client.access_token = ""
    need_login = forticloud_client.get_if_need_to_do_login()
    assert need_login is True


def get_if_need_to_do_login_return_true_if_expired_token_test(forticloud_client):
    forticloud_client.access_token = "Test"
    forticloud_client.expiration_date_token = datetime.utcnow() - timedelta(days=1)
    need_login = forticloud_client.get_if_need_to_do_login()
    assert need_login is True


def get_if_need_to_do_login_return_false_test(forticloud_client):
    forticloud_client.access_token = "Test"
    forticloud_client.expiration_date_token = datetime.utcnow() + timedelta(days=1)
    need_login = forticloud_client.get_if_need_to_do_login()
    assert need_login is False


def get_expiration_date_for_token_return_not_none_test(forticloud_client):
    date = forticloud_client.get_expiration_date_for_token(60)
    assert date is not None


async def get_response_device_return_not_none_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=[])
    response = await forticloud_client.get_response_device(device="")
    assert response is not None


async def get_response_device_return_list_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=[])
    response = await forticloud_client.get_response_device(device="")
    assert type(response) == list


async def device_strategy_return_not_none_test(forticloud_client):
    forticloud_client.get_devices = AsyncMock()
    devices = await forticloud_client.device_strategy(device="", network_id="")
    assert devices is not None


async def device_strategy_return_list_test(forticloud_client):
    forticloud_client.get_devices = AsyncMock()
    devices = await forticloud_client.device_strategy(device="", network_id="")
    assert type(devices) == list


async def device_strategy_call_device_access_points_test(forticloud_client):
    forticloud_client.get_devices = AsyncMock()
    await forticloud_client.device_strategy(device="access_points", network_id="")
    forticloud_client.get_devices.assert_called_once_with(
        response_content_type="text/plain", url_api="/fap/access_points/", network_id="", serial_number=""
    )


async def device_strategy_call_device_networks_test(forticloud_client):
    forticloud_client.get_devices = AsyncMock()
    await forticloud_client.device_strategy(device="networks", network_id="")
    forticloud_client.get_devices.assert_called_once_with(url_api="", serial_number="")


async def device_strategy_call_device_switch_test(forticloud_client):
    forticloud_client.get_devices = AsyncMock()
    await forticloud_client.device_strategy(device="switches", network_id="")
    forticloud_client.get_devices.assert_called_once_with(
        url_api="/fsw/switch/switches/", network_id="", serial_number=""
    )


async def login_return_none_test(forticloud_client):
    response_mock = Mock()
    response_mock.status = HTTPStatus.OK
    response_mock.json = AsyncMock(return_value=RESPONSE_LOGIN)
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)

    result = await forticloud_client.login()
    assert result is None


async def login_return_add_access_token_test(forticloud_client):
    response_mock = Mock()
    response_mock.status = HTTPStatus.OK
    response_mock.json = AsyncMock(return_value=RESPONSE_LOGIN)
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    await forticloud_client.login()
    assert forticloud_client.access_token == RESPONSE_LOGIN["access_token"]


async def login_return_add_expiration_date_test(forticloud_client):
    await forticloud_client.create_session()
    response_mock = Mock()
    response_mock.status = HTTPStatus.OK
    response_mock.json = AsyncMock(return_value=RESPONSE_LOGIN)
    forticloud_client.get_expiration_date_for_token = Mock()
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    await forticloud_client.login()
    forticloud_client.get_expiration_date_for_token.assert_called_with(RESPONSE_LOGIN["expires_in"])


async def login_not_ok_test(forticloud_client):
    login_exception = ""
    response_mock = Mock()
    response_mock.status = HTTPStatus.INTERNAL_SERVER_ERROR
    response_mock.json = AsyncMock(return_value=RESPONSE_LOGIN)
    forticloud_client.get_expiration_date_for_token = Mock()
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    try:
        await forticloud_client.login()
    except LoginError as e:
        login_exception = e
    assert login_exception


async def get_device_return_not_none_test(forticloud_client):
    forticloud_client.get_if_need_to_do_login = Mock(return_value=False)
    response_mock = Mock()
    response_mock.status = HTTPStatus.OK
    response_mock.json = AsyncMock(return_value=RESPONSE_DEVICES)
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    devices_response = await forticloud_client.get_devices(serial_number="")
    assert devices_response is not None


async def get_device_do_login_test(forticloud_client):
    await forticloud_client.create_session()
    forticloud_client.get_if_need_to_do_login = Mock(return_value=True)
    response_mock = Mock()
    response_mock.status = HTTPStatus.OK
    response_mock.json = AsyncMock(return_value=RESPONSE_DEVICES)
    forticloud_client.login = AsyncMock()
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    await forticloud_client.get_devices(serial_number="")
    forticloud_client.login.assert_called()


async def get_device_return_not_empty_body_test(forticloud_client):
    await forticloud_client.create_session()
    forticloud_client.get_if_need_to_do_login = Mock(return_value=False)
    response_mock = Mock()
    response_mock.status = HTTPStatus.OK
    response_mock.json = AsyncMock(return_value=RESPONSE_DEVICES)
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    devices_response = await forticloud_client.get_devices(serial_number="")
    assert len(devices_response["body"]) > 0


async def get_device_return_empty_when_status_is_not_ok_test(forticloud_client):
    forticloud_client.get_if_need_to_do_login = Mock(return_value=False)
    response_mock = Mock()
    response_mock.status = HTTPStatus.INTERNAL_SERVER_ERROR
    response_mock.json = AsyncMock(return_value=RESPONSE_DEVICES)
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    devices_response = await forticloud_client.get_devices(serial_number="")
    assert len(devices_response["body"]) == 0


async def get_device_return_same_status_that_call_when_is_not_ok_test(forticloud_client):
    await forticloud_client.create_session()
    forticloud_client.get_if_need_to_do_login = Mock(return_value=False)
    response_mock = Mock()
    response_mock.status = HTTPStatus.INTERNAL_SERVER_ERROR
    response_mock.json = AsyncMock(return_value=RESPONSE_DEVICES)
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    devices_response = await forticloud_client.get_devices(serial_number="")
    assert devices_response["status"] == HTTPStatus.INTERNAL_SERVER_ERROR


async def get_devices_not_ok_test(forticloud_client):
    await forticloud_client.create_session()
    forticloud_client.get_if_need_to_do_login = Mock(return_value=True)
    response_mock = Mock()
    response_mock.status = HTTPStatus.INTERNAL_SERVER_ERROR
    response_mock.json = AsyncMock(return_value=Exception)
    forticloud_client.get_expiration_date_for_token = Mock()
    forticloud_client.session = AsyncMock()
    forticloud_client.create_session = AsyncMock()
    forticloud_client.close_session = AsyncMock()
    forticloud_client.session.request = AsyncMock(return_value=response_mock)
    devices_response = await forticloud_client.get_devices(serial_number="")
    assert devices_response["status"] == HTTPStatus.INTERNAL_SERVER_ERROR


async def get_device_status_return_not_none_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock()
    device_status_response = await forticloud_client.get_device_status(network_id="", device="", serial_number="")
    assert device_status_response is not None


async def get_device_status_return_response_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_status(network_id="", device="", serial_number="")
    assert type(device_status_response) is dict


async def get_device_status_return_status_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_status(network_id="", device="", serial_number="")
    assert "status" in device_status_response


async def get_device_status_return_same_request_status_than_strategy_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_status(network_id="", device="", serial_number="")
    assert RESPONSE_DEVICE["status"] == device_status_response["status"]


async def get_device_status_return_body_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_status(network_id="", device="", serial_number="")
    assert "body" in device_status_response


async def get_device_status_return_body_with_status_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_status(network_id="", device="", serial_number="")
    assert "status_device" in device_status_response["body"]


async def get_device_info_return_not_none_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_info(network_id="", device="", serial_number="")
    assert device_status_response is not None


async def get_device_info_return_dict_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_info(network_id="", device="", serial_number="")
    assert type(device_status_response) is dict


async def get_device_info_return_status_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_info(network_id="", device="", serial_number="")
    assert "status" in device_status_response


async def get_device_info_return_body_test(forticloud_client):
    forticloud_client.device_strategy = AsyncMock(return_value=RESPONSE_DEVICE)
    device_status_response = await forticloud_client.get_device_info(network_id="", device="", serial_number="")
    assert "body" in device_status_response


RESPONSE_LOGIN = {"access_token": "example token", "expires_in": 3600}
RESPONSE_DEVICES = {"result": [{"id": "device id"}]}
RESPONSE_DEVICE = {"status": 200, "body": {"status": "offline"}}
