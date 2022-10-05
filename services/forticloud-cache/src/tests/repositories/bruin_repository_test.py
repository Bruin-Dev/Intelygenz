from unittest.mock import AsyncMock, Mock

import pytest

from application.repositories.bruin_repository import BruinRepository

LIST_OF_DEVICES = [{"serial_number": "serial_number_test"}]
CLIENT_ID = 2222
CUSTOMER_INFO = [{"client_id": CLIENT_ID}]
SERIAL_NUMBER = "SN1"
MANAGEMENTS_STATUS = "test"


@pytest.fixture(scope="function")
def bruin_repository_instance(bruin_client_instance):
    return BruinRepository(bruin_client=bruin_client_instance)


async def get_list_of_devices_with_client_id_not_return_none_test(bruin_repository_instance):
    bruin_repository_instance.get_client_id_from_device = AsyncMock(return_value=CLIENT_ID)
    list_of_devices_with_client_id = await bruin_repository_instance.get_list_of_devices_with_client_id(
        list_of_devices=LIST_OF_DEVICES
    )
    assert list_of_devices_with_client_id is not None


async def get_list_of_devices_with_client_id_return_list_test(bruin_repository_instance):
    bruin_repository_instance.get_client_id_from_device = AsyncMock(return_value=CLIENT_ID)
    list_of_devices_with_client_id = await bruin_repository_instance.get_list_of_devices_with_client_id(
        list_of_devices=LIST_OF_DEVICES
    )
    assert type(list_of_devices_with_client_id) is list


async def get_list_of_devices_with_client_id_return_not_empty_list_test(bruin_repository_instance):
    bruin_repository_instance.get_client_id_from_device = AsyncMock(return_value=CLIENT_ID)
    list_of_devices_with_client_id = await bruin_repository_instance.get_list_of_devices_with_client_id(
        list_of_devices=LIST_OF_DEVICES
    )
    assert len(list_of_devices_with_client_id) > 0


async def get_list_of_devices_with_client_id_return_empty_list_where_not_found_client_test(bruin_repository_instance):
    bruin_repository_instance.get_client_id_from_device = AsyncMock(return_value=None)
    list_of_devices_with_client_id = await bruin_repository_instance.get_list_of_devices_with_client_id(
        list_of_devices=LIST_OF_DEVICES
    )
    assert len(list_of_devices_with_client_id) == 0


async def get_client_id_from_device_return_not_none_test(bruin_repository_instance):
    bruin_repository_instance.bruin_client.get_customer_info_from_serial = AsyncMock(return_value=CUSTOMER_INFO)
    list_of_devices_with_client_id = await bruin_repository_instance.get_client_id_from_device(
        device=LIST_OF_DEVICES[0]
    )
    assert list_of_devices_with_client_id is not None


async def get_client_id_from_device_return_int_test(bruin_repository_instance):
    bruin_repository_instance.bruin_client.get_customer_info_from_serial = AsyncMock(return_value=CUSTOMER_INFO)
    list_of_devices_with_client_id = await bruin_repository_instance.get_client_id_from_device(
        device=LIST_OF_DEVICES[0]
    )
    assert type(list_of_devices_with_client_id) is int


async def get_client_id_from_device_return_none_test(bruin_repository_instance):
    bruin_repository_instance.bruin_client.get_customer_info_from_serial = AsyncMock(return_value=None)
    list_of_devices_with_client_id = await bruin_repository_instance.get_client_id_from_device(
        device=LIST_OF_DEVICES[0]
    )
    assert list_of_devices_with_client_id is None


async def get_management_status_for_device_return_not_none_test(bruin_repository_instance):
    bruin_repository_instance.bruin_client.get_management_status = AsyncMock(return_value=MANAGEMENTS_STATUS)
    management_status = await bruin_repository_instance.get_management_status_for_device(
        client_id=CLIENT_ID, serial_number=SERIAL_NUMBER
    )
    assert management_status is not None


async def get_management_status_for_device_return_str_test(bruin_repository_instance):
    bruin_repository_instance.bruin_client.get_management_status = AsyncMock(return_value=MANAGEMENTS_STATUS)
    management_status = await bruin_repository_instance.get_management_status_for_device(
        client_id=CLIENT_ID, serial_number=SERIAL_NUMBER
    )
    assert type(management_status) is str


async def get_management_status_for_device_return_none_when_dont_found_test(bruin_repository_instance):
    bruin_repository_instance.bruin_client.get_management_status = AsyncMock(return_value=None)
    management_status = await bruin_repository_instance.get_management_status_for_device(
        client_id=CLIENT_ID, serial_number=SERIAL_NUMBER
    )
    assert management_status is None
