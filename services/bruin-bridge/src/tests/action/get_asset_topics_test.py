from unittest.mock import ANY, AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_asset_topics import *
from application.clients.bruin_session import BruinResponse
from application.repositories.utils_repository import to_json_bytes


class TestGetAssetTopics:
    @pytest.mark.asyncio
    async def get_asset_topics_ok_test(self, get_asset_topics, mocked_response):
        # Given
        request = {
            "body": {
                "client_id": 321,
                "service_number": "VC1234567",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        # When
        await get_asset_topics(request_msg)

        # Then
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": mocked_response.body, "status": mocked_response.status})
        )

    @pytest.mark.asyncio
    async def get_asset_topics_without_body_test(self, get_asset_topics):
        # Given
        request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        # When
        await get_asset_topics(request_msg)

        # Then
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": NO_BODY_MSG, "status": HTTPStatus.BAD_REQUEST})
        )

    @pytest.mark.asyncio
    async def get_asset_topics_without_client_id_test(self, get_asset_topics):
        # Given
        request = {
            "body": {
                "service_number": "VC1234567",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        # When
        await get_asset_topics(request_msg)

        # Then
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": MISSING_PARAMS_MSG, "status": HTTPStatus.BAD_REQUEST})
        )

    @pytest.mark.asyncio
    async def get_asset_topics_without_service_number_test(self, get_asset_topics):
        # Given
        request = {
            "body": {
                "client_id": 123,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        # When
        await get_asset_topics(request_msg)

        # Then
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": MISSING_PARAMS_MSG, "status": HTTPStatus.BAD_REQUEST})
        )

    @pytest.mark.asyncio
    async def get_asset_topics_with_string_client_id_test(self, get_asset_topics):
        # Given
        request = {
            "body": {
                "client_id": "a_string",
                "service_number": "VC1234567",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        # When
        await get_asset_topics(request_msg)

        # Then
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": WRONG_CLIENT_ID_MSG, "status": HTTPStatus.BAD_REQUEST})
        )

    @pytest.mark.asyncio
    async def get_asset_topics_with_empty_service_number_test(self, get_asset_topics):
        # Given
        request = {
            "body": {
                "client_id": 1234,
                "service_number": "",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(request)

        # When
        await get_asset_topics(request_msg)

        # Then
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": EMPTY_SERVICE_NUMBER_MSG, "status": HTTPStatus.BAD_REQUEST})
        )


#
# Fixtures
#


@pytest.fixture
def get_asset_topics(mocked_response):
    bruin_repository = Mock()
    bruin_repository.get_asset_topics = AsyncMock(return_value=mocked_response)
    return GetAssetTopics(bruin_repository)


@pytest.fixture
def mocked_response():
    return BruinResponse(
        status=HTTPStatus.OK,
        body={
            "callTypes": [
                {
                    "callType": "CHG",
                    "callTypeDescription": "Service Changes",
                    "category": "053",
                    "categoryDescription": "Add Additional Lines",
                },
            ]
        },
    )
