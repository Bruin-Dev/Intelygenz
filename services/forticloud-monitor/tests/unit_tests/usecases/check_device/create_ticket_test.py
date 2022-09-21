from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError

from clients.http_client import HttpClient, HttpResponse
from shared.errors import UnexpectedResponseError, UnexpectedStatusError
from usecases.check_device import STATUS_DESCRIPTIONS, CreateTicket


async def tickets_are_properly_created_test(scenario, any_response, any_device_id):
    any_response.body = '{"assets":[{"ticketId":1}]}'
    create_ticket = scenario(send=AsyncMock(return_value=any_response))

    # when
    created_ticket = await create_ticket(any_device_id)

    # then
    assert created_ticket.ticket_id == "1"


async def status_descriptions_are_properly_built_test(scenario, any_response, any_device_id):
    any_response.body = '{"assets":[{"ticketId":1,"errorCode":409}]}'
    create_ticket = scenario(send=AsyncMock(return_value=any_response))

    # when
    created_ticket = await create_ticket(any_device_id)

    # then
    assert created_ticket.status_description == STATUS_DESCRIPTIONS[409]


async def unknown_status_descriptions_are_properly_built_test(scenario, any_response, any_device_id):
    any_response.body = '{"assets":[{"ticketId":1,"errorCode":1}]}'
    create_ticket = scenario(send=AsyncMock(return_value=any_response))

    # when
    created_ticket = await create_ticket(any_device_id)

    # then
    assert created_ticket.status_description is None


@pytest.mark.parametrize(
    "response",
    [
        HttpResponse(200, '{"items":[{"ticketId":1}]}'),
        HttpResponse(200, '{"assets":[{"ticketId":1}]}'),
        HttpResponse(200, '{"assets":[{"ticketId":1}],"any_field":"any_value"}'),
        HttpResponse(200, '{"assets":[{"ticketId":1,"errorCode":1}]}'),
        HttpResponse(200, '{"assets":[{"ticketId":1,"errorCode":1,"any_field":"any_value"}]}'),
        HttpResponse(200, '{"assets":[{"ticketId":1}],"items":[{"ticketId":2}]}'),
    ],
    ids=[
        "items response",
        "assets response",
        "assets response with extra root fields",
        "assets response with errorCode",
        "assets response with extra asset fields",
        "assets and items",
    ],
)
async def responses_are_properly_parsed_test(scenario, response, any_device_id):
    # given
    create_ticket = scenario(send=AsyncMock(return_value=response))

    # # when
    created_ticket = await create_ticket(any_device_id)

    # then
    assert created_ticket.ticket_id == "1"


async def wrong_data_raises_an_exception_test(scenario, any_device_id):
    # given
    any_device_id.client_id = "any_string"
    create_ticket = scenario()

    # then
    with pytest.raises(ValidationError):
        await create_ticket(any_device_id)


async def client_errors_are_properly_propagated_test(scenario, any_device_id, any_exception):
    # given
    create_ticket = scenario(send=AsyncMock(side_effect=any_exception))

    # then
    with pytest.raises(any_exception):
        await create_ticket(any_device_id)


async def unexpected_response_status_raise_an_exception_test(scenario, any_device_id, any_response):
    # given
    any_response.status = HTTPStatus.BAD_REQUEST
    create_ticket = scenario(send=AsyncMock(return_value=any_response))

    # then
    with pytest.raises(UnexpectedStatusError):
        await create_ticket(any_device_id)


@pytest.mark.parametrize(
    "response",
    [
        HttpResponse(200, body="any_string"),
        HttpResponse(200, body='{"syntax_error":1'),
        HttpResponse(200, body='{"unknown_field":1}'),
        HttpResponse(200, body='{"assets":[{"unknown_field":1}]}'),
        HttpResponse(200, body='{"assets":[{"ticketId":"any_string"}]}'),
        HttpResponse(200, body='{"assets":{"ticketId":1}}'),
        HttpResponse(200, body='{"assets":[],"items":[]}'),
    ],
    ids=[
        "non json body",
        "syntax error body",
        "required fields missing",
        "wrong asset field type",
        "required asset fields missing",
        "wrong assets type",
        "empty assets and items",
    ],
)
async def unexpected_responses_raise_an_exception_test(scenario, any_device_id, response):
    # given
    create_ticket = scenario(send=AsyncMock(return_value=response))

    # then
    with pytest.raises(UnexpectedResponseError):
        await create_ticket(any_device_id)


@pytest.fixture
def scenario(any_response):
    def builder(send: AsyncMock = AsyncMock(return_value=any_response)):
        http_client = Mock(HttpClient)
        http_client.send = send

        return CreateTicket(http_client)

    return builder


@pytest.fixture
def any_response():
    return HttpResponse(HTTPStatus.OK, '{"assets": [{"ticketID": hash("any_ticket_id")}]}')
