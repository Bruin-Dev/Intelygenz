from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest
from bruin_client import BruinClient, BruinRequest, BruinResponse
from pydantic import ValidationError

from application.models.ticket import CreatedTicket, TicketStatus
from application.repositories import BruinRepository, UnexpectedResponseError, UnexpectedStatusError


async def repair_tickets_are_properly_posted_test(any_bruin_repository, any_response, any_device_id):
    any_device_id.client_id = "1"
    any_device_id.service_number = "any_service_number"
    send = AsyncMock(return_value=any_response)
    bruin_repository = any_bruin_repository(send=send)

    # when
    await bruin_repository.post_repair_ticket(any_device_id)

    # then
    send.assert_awaited_once_with(
        BruinRequest(
            method="POST",
            path="/api/Ticket/repair",
            json="{"
            '"ClientID": 1, '
            '"WTNs": ["any_service_number"], '
            '"RequestDescription": "MetTel\'s IPA -- Service Outage Trouble"'
            "}",
        )
    )


@pytest.mark.parametrize(
    "response_text",
    [
        '{"items":[{"ticketId":1}]}',
        '{"assets":[{"ticketId":1}]}',
        '{"assets":[{"ticketId":1}],"any_field":"any_value"}',
        '{"assets":[{"ticketId":1,"errorCode":1}]}',
        '{"assets":[{"ticketId":1,"errorCode":1,"any_field":"any_value"}]}',
        '{"assets":[{"ticketId":1}],"items":[{"ticketId":2}]}',
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
async def responses_are_properly_parsed_test(any_bruin_repository, response_text, any_device_id):
    # given
    response = BruinResponse(status=HTTPStatus.OK, text=response_text)
    bruin_repository = any_bruin_repository(send=AsyncMock(return_value=response))

    # # when
    created_ticket = await bruin_repository.post_repair_ticket(any_device_id)

    # then
    assert created_ticket == CreatedTicket(ticket_id="1", ticket_status=TicketStatus.CREATED)


@pytest.mark.parametrize(
    ["response_text", "expected_status"],
    [
        ('{"items":[{"ticketId":1,"errorCode":1}]}', TicketStatus.CREATED),
        ('{"items":[{"ticketId":1,"errorCode":200}]}', TicketStatus.CREATED),
        ('{"items":[{"ticketId":1,"errorCode":409}]}', TicketStatus.IN_PROGRESS),
        ('{"items":[{"ticketId":1,"errorCode":471}]}', TicketStatus.FAILED_REOPENING),
        ('{"items":[{"ticketId":1,"errorCode":472}]}', TicketStatus.REOPENED),
        ('{"items":[{"ticketId":1,"errorCode":473}]}', TicketStatus.REOPENED_SAME_LOCATION),
    ],
    ids=[
        "unknown errorCode",
        "CREATED errorCode",
        "IN_PROGRESS errorCode",
        "FAILED_REOPENING errorCode",
        "REOPENED errorCode",
        "REOPENED_SAME_LOCATION errorCode",
    ],
)
async def ticket_status_are_properly_built_test(
    any_bruin_repository,
    response_text,
    expected_status,
    any_device_id,
):
    response = BruinResponse(status=HTTPStatus.OK, text=response_text)
    bruin_repository = any_bruin_repository(send=AsyncMock(return_value=response))

    # when
    created_ticket = await bruin_repository.post_repair_ticket(any_device_id)

    # then
    assert created_ticket.ticket_status == expected_status


async def wrong_data_raises_an_exception_test(any_bruin_repository, any_device_id):
    # given
    any_device_id.client_id = "any_string"
    bruin_repository = any_bruin_repository()

    # then
    with pytest.raises(ValidationError):
        await bruin_repository.post_repair_ticket(any_device_id)


async def client_errors_are_properly_propagated_test(any_bruin_repository, any_device_id, any_exception):
    # given
    bruin_repository = any_bruin_repository(send=AsyncMock(side_effect=any_exception))

    # then
    with pytest.raises(any_exception):
        await bruin_repository.post_repair_ticket(any_device_id)


async def unexpected_response_status_raise_an_exception_test(any_bruin_repository, any_device_id, any_response):
    # given
    any_response.status = HTTPStatus.BAD_REQUEST
    bruin_repository = any_bruin_repository(send=AsyncMock(return_value=any_response))

    # then
    with pytest.raises(UnexpectedStatusError):
        await bruin_repository.post_repair_ticket(any_device_id)


@pytest.mark.parametrize(
    "response_text",
    [
        "any_string",
        '{"syntax_error":1',
        "{}",
        '{"assets":{}}',
        '{"assets":[1]}',
        '{"assets":[{}]}',
        '{"assets":[{"ticketId":{}}]}',
        '{"assets":[{"ticketId":"any_string","errorCode":"any_string"}]}',
        '{"assets":[],"items":[]}',
    ],
    ids=[
        "non json body",
        "syntax error body",
        "required fields missing",
        "wrong assets type",
        "wrong asset type",
        "required asset fields missing",
        "wrong ticketId type",
        "wrong errorCode type",
        "empty assets and items",
    ],
)
async def unexpected_responses_raise_an_exception_test(any_bruin_repository, any_device_id, response_text):
    # given
    response = BruinResponse(status=HTTPStatus.OK, text=response_text)
    bruin_repository = any_bruin_repository(send=AsyncMock(return_value=response))

    # then
    with pytest.raises(UnexpectedResponseError):
        await bruin_repository.post_repair_ticket(any_device_id)


@pytest.fixture
def any_bruin_repository(any_response):
    def builder(send: AsyncMock = AsyncMock(return_value=any_response)):
        bruin_client = Mock(BruinClient)
        bruin_client.send = send

        return BruinRepository(bruin_client)

    return builder


@pytest.fixture
def any_response():
    return BruinResponse(status=HTTPStatus.OK, text='{"assets":[{"ticketId":1}]}')
