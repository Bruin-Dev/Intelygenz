import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from unittest.mock import ANY, AsyncMock

import pytest
from bruin_client import BruinRequest, BruinResponse

from application.domain.device import DeviceId, DeviceType
from application.domain.service_number import ServiceNumber
from application.domain.task import TicketTask
from application.repositories.bruin_repository_models.find_ticket import (
    BruinTicket,
    BruinTicketData,
    BruinTicketDetail,
    BruinTicketNote,
    BruinTicketsResponse,
    FindTicketQuery,
)


def any_bruin_ticket_detail(detail_id: int = 1, detail_value: str = "any", detail_status: str = "any"):
    return BruinTicketDetail(detailID=detail_id, detailValue=detail_value, detailStatus=detail_status)


@pytest.mark.parametrize("expected_status", ["any_status_A", "any_status_B", "any_status_C"])
async def tickets_are_properly_queried_test(
    any_bruin_repository,
    any_query,
    any_device_id,
    expected_status,
):
    # given
    device_id = any_device_id(client_id="any_client_id", service_number=ServiceNumber("any_service_number"))
    query = any_query(
        ticket_topic="any_ticket_topic", device_id=device_id, statuses=["any_status_A", "any_status_B", "any_status_C"]
    )
    send = AsyncMock()
    bruin_repository = any_bruin_repository(send=send)

    # when
    await bruin_repository.find_ticket(query)

    # then
    send.assert_any_await(
        BruinRequest(
            method="GET",
            path="/api/Ticket/basic",
            query_params={
                "TicketStatus": expected_status,
                "TicketTopic": "any_ticket_topic",
                "ClientId": "any_client_id",
                "ServiceNumber": "any_service_number",
            },
        )
    )


@pytest.mark.parametrize(
    ["bruin_response", "expected_bruin_tickets"],
    [
        ("{}", BruinTicketsResponse()),
        ('{"any_field": "any_value"}', BruinTicketsResponse()),
        ('{"responses":[]}', BruinTicketsResponse()),
        ('{"responses":[{}]}', BruinTicketsResponse()),
        ('{"responses":[{"any_field": "any_value"}]}', BruinTicketsResponse()),
        (
            '{"responses":[{'
            '"ticketID": "non_int_value", "createdBy": "any_user", "createDate": "10/10/2022 8:58:28 AM"'
            "}]}",
            BruinTicketsResponse(),
        ),
        (
            '{"responses":[{"ticketID": 1234, "createdBy": "any_user", "createDate": "non_datetime_value"}]}',
            BruinTicketsResponse(),
        ),
        (
            '{"responses":[{"ticketID": 1234, "createdBy": [], "createDate": "10/10/2022 8:58:28 AM"}]}',
            BruinTicketsResponse(),
        ),
        ('{"responses":[{"ticketID": 1234, "createdBy": "any_user"}]}', BruinTicketsResponse()),
        ('{"responses":[{"ticketID": 1234, "createDate": "10/10/2022 8:58:28 AM"}]}', BruinTicketsResponse()),
        ('{"responses":[{"createdBy": "any_user", "createDate": "10/10/2022 8:58:28 AM"}]}', BruinTicketsResponse()),
        (
            '{"responses":[{"ticketID": 1234, "createdBy": "any_user", "createDate": "10/10/2022 8:58:28 AM"}]}',
            BruinTicketsResponse(
                responses=[
                    BruinTicket(
                        ticketID=1234,
                        createdBy="any_user",
                        createDate=datetime(2022, 10, 10, 8, 58, 28, tzinfo=timezone.utc),
                    )
                ]
            ),
        ),
    ],
    ids=[
        "empty_json",
        "extra_root_fields",
        "empty_responses",
        "empty_response",
        "extra_response_fields",
        "wrong_ticket_id_type",
        "wrong_create_date_type",
        "wrong_created_by_type",
        "missing_create_date",
        "missing_created_by",
        "missing_ticket_id",
        "full_data_response",
    ],
)
async def bruin_tickets_responses_are_properly_parsed_test(bruin_response, expected_bruin_tickets):
    assert BruinTicketsResponse.parse_raw(bruin_response) == expected_bruin_tickets


async def only_ok_bruin_ticket_responses_are_processed_test(
    any_bruin_repository,
    any_query,
    any_valid_tickets_response,
    any_bruin_response,
):
    # given
    query = any_query(statuses=["A", "B", "C"])
    send = AsyncMock(
        side_effect=[
            BruinResponse(status=500, text=""),
            BruinResponse(status=400, text=""),
            any_valid_tickets_response(ticket_id=1234),
            any_bruin_response,
        ]
    )
    bruin_repository = any_bruin_repository(send=send)

    # when
    await bruin_repository.find_ticket(query)

    # then
    send.assert_any_await(BruinRequest(method="GET", path="/api/Ticket/1234/details"))


async def unexpected_bruin_ticket_responses_arent_processed_test(
    any_bruin_repository,
    any_query,
    any_valid_tickets_response,
    any_bruin_response,
):
    # given
    query = any_query(statuses=["A", "B", "C"])
    send = AsyncMock(
        side_effect=[
            Exception,
            "any_object",
            any_valid_tickets_response(ticket_id=1234),
            any_bruin_response,
        ]
    )
    bruin_repository = any_bruin_repository(send=send)

    # when
    await bruin_repository.find_ticket(query)

    # then
    send.assert_any_await(BruinRequest(method="GET", path="/api/Ticket/1234/details"))


async def only_well_formed_bruin_ticket_responses_are_processed_test(
    any_bruin_repository,
    any_query,
    any_valid_tickets_response,
    any_bruin_response,
):
    # given
    query = any_query(statuses=["A", "B", "C"])
    send = AsyncMock(
        side_effect=[
            BruinResponse(status=200, text="non_json_response"),
            BruinResponse(status=200, text='{"malformed_json"}'),
            any_valid_tickets_response(ticket_id=1234),
            any_bruin_response,
        ]
    )
    bruin_repository = any_bruin_repository(send=send)

    # when
    await bruin_repository.find_ticket(query)

    # then
    send.assert_any_await(BruinRequest(method="GET", path="/api/Ticket/1234/details"))


async def no_ticket_was_found_test(any_bruin_repository, any_query):
    # given
    bruin_repository = any_bruin_repository(send=AsyncMock(return_value=BruinResponse(status=200, text="{}")))

    # when
    ticket = await bruin_repository.find_ticket(any_query())

    # then
    assert not ticket


async def only_first_bruin_tickets_are_processed(
    any_bruin_repository,
    any_query,
    any_valid_tickets_response,
    any_bruin_response,
):
    # given
    any_query.statuses = ["status_A", "status_B", "status_C"]
    send = AsyncMock(
        side_effect=[
            any_valid_tickets_response(ticket_id=1),
            any_valid_tickets_response(ticket_id=2),
            any_valid_tickets_response(ticket_id=3),
            any_bruin_response,
        ]
    )
    bruin_repository = any_bruin_repository(send=send, query=any_query)

    # when
    await bruin_repository.find_ticket(any_query)

    # then
    send.assert_any_await(BruinRequest(method="GET", path="/api/Ticket/1/details"))


async def no_ticket_created_by_the_given_user_was_found_test(
    any_bruin_repository,
    any_query,
    any_valid_tickets_response,
):
    # given
    query = any_query(created_by="given_user")
    bruin_repository = any_bruin_repository(
        send=AsyncMock(return_value=any_valid_tickets_response(created_by="different_user"))
    )

    # when
    ticket = await bruin_repository.find_ticket(query)

    # then
    assert not ticket


async def ticket_data_is_properly_queried_test(
    any_bruin_repository,
    any_query,
    any_valid_tickets_response,
    any_bruin_response,
):
    # given
    query = any_query(statuses=["any_status"])
    send = AsyncMock(side_effect=[any_valid_tickets_response(ticket_id=1234), any_bruin_response])
    bruin_repository = any_bruin_repository(send=send)

    # when
    await bruin_repository.find_ticket(query)

    # then
    send.assert_any_await(BruinRequest(method="GET", path="/api/Ticket/1234/details"))


@pytest.mark.parametrize(
    ["bruin_response", "expected_ticket_data"],
    [
        ("{}", BruinTicketData()),
        ('{"any_field": "any_value"}', BruinTicketData()),
        ('{"ticketDetails":[]}', BruinTicketData()),
        ('{"ticketDetails":[{}]}', BruinTicketData()),
        ('{"ticketDetails":[{"any_field": "any_value"}]}', BruinTicketData()),
        (
            '{"ticketDetails":[{"detailID": "non_int_value", "devailValue": "any", "detailStatus": "any"}]}',
            BruinTicketData(),
        ),
        ('{"ticketDetails":[{"detailValue": [], "detailID": 1234, "detailStatus": "any"}]}', BruinTicketData()),
        ('{"ticketDetails":[{"detailStatus": [], "detailID": 1234, "detailValue": "any"}]}', BruinTicketData()),
        ('{"ticketDetails":[{"detailID": 1234, "detailValue": "any_value"}]}', BruinTicketData()),
        ('{"ticketDetails":[{"detailID": 1234, "detailStatus": "any_status"}]}', BruinTicketData()),
        ('{"ticketDetails":[{"detailValue": "any_value", "detailStatus": "any_status"}]}', BruinTicketData()),
        (
            '{"ticketDetails":[{"detailID": 1234, "detailValue": "any_value", "detailStatus": "any_status"}]}',
            BruinTicketData(
                ticketDetails=[BruinTicketDetail(detailID=1234, detailValue="any_value", detailStatus="any_status")]
            ),
        ),
        ('{"ticketNotes":[]}', BruinTicketData()),
        ('{"ticketNotes":[{}]}', BruinTicketData()),
        ('{"ticketNotes":[{"any_field": "any_value"}]}', BruinTicketData()),
        (
            '{"ticketNotes":[{"noteValue": [], "createdDate": "2022-10-10T03:56:23.023-04:00", "serviceNumber": []}]}',
            BruinTicketData(),
        ),
        (
            '{"ticketNotes":[{"createdDate": "non_datetime_value", "noteValue": "any", "serviceNumber": []}]}',
            BruinTicketData(),
        ),
        (
            '{"ticketNotes":[{'
            '"serviceNumber": "non_list_value", "createdDate": "2022-10-10T03:56:23.023-04:00", "noteValue": "any"'
            "}]}",
            BruinTicketData(),
        ),
        (
            '{"ticketNotes":[{'
            '"noteValue": "any_value", "createdDate": "2022-10-10T03:56:23.023-04:00", "serviceNumber": [{}]'
            "}]}",
            BruinTicketData(),
        ),
        ('{"ticketNotes":[{"noteValue": "any_value", "serviceNumber": []}]}', BruinTicketData()),
        (
            '{"ticketNotes":[{"noteValue": "any_value", "createdDate": "2022-10-10T03:56:23.023-04:00"}]}',
            BruinTicketData(),
        ),
        (
            '{"ticketNotes":[{"createdDate": "2022-10-10T03:56:23.023-04:00", "serviceNumber": []}]}',
            BruinTicketData(),
        ),
        (
            '{"ticketNotes":[{'
            '"noteValue": "any_value", '
            '"createdDate": "2022-10-10T03:56:23.023-04:00", '
            '"serviceNumber": ["any_service_number"]'
            "}]}",
            BruinTicketData(
                ticketNotes=[
                    BruinTicketNote(
                        noteValue="any_value",
                        createdDate=datetime(2022, 10, 10, 3, 56, 23, 23000, tzinfo=timezone(timedelta(hours=-4))),
                        serviceNumber=["any_service_number"],
                    )
                ]
            ),
        ),
        (
            "{"
            '"ticketDetails":[{"detailID": 1234, "detailValue": "any_value", "detailStatus": "any_status"}], '
            '"ticketNotes":[{'
            '"noteValue": "any_value", '
            '"createdDate": "2022-10-10T03:56:23.023-04:00", '
            '"serviceNumber": ["any_service_number"]'
            "}]"
            "}",
            BruinTicketData(
                ticketDetails=[BruinTicketDetail(detailID=1234, detailValue="any_value", detailStatus="any_status")],
                ticketNotes=[
                    BruinTicketNote(
                        noteValue="any_value",
                        createdDate=datetime(2022, 10, 10, 3, 56, 23, 23000, tzinfo=timezone(timedelta(hours=-4))),
                        serviceNumber=["any_service_number"],
                    )
                ],
            ),
        ),
    ],
    ids=[
        "empty_json",
        "extra_root_fields",
        "empty_ticket_details",
        "empty_ticket_detail",
        "extra_ticket_detail_fields",
        "wrong_ticket_detail_id_type",
        "wrong_ticket_detail_value_type",
        "wrong_ticket_detail_status_type",
        "missing_ticket_detail_status",
        "missing_ticket_detail_value",
        "missing_ticket_detail_id",
        "single_ticket_detail",
        "empty_ticket_notes",
        "empty_ticket_note",
        "extra_ticket_note_fields",
        "wrong_ticket_note_value_type",
        "wrong_ticket_note_created_date_type",
        "wrong_ticket_note_service_number_type",
        "wrong_ticket_note_service_number_item_type",
        "missing_ticket_note_created_date_status",
        "missing_ticket_note_service_number",
        "missing_ticket_note_value",
        "single_ticket_note",
        "single_ticket_detail_and_ticket_note",
    ],
)
async def ticket_data_is_properly_parsed_test(bruin_response, expected_ticket_data):
    assert BruinTicketData.parse_raw(bruin_response) == expected_ticket_data


async def ticket_task_data_is_properly_built_test():
    # given
    ticket_detail = BruinTicketDetail(detailID=1, detailValue="any_service_number", detailStatus="any_status")
    bruin_ticket_data = BruinTicketData(ticketDetails=[ticket_detail])

    # when
    tasks = bruin_ticket_data.build_ticket_tasks_with(
        task_auto_resolution_grace_period=timedelta(days=1),
        task_max_auto_resolutions=1,
    )
    assert tasks == {
        "any_service_number": TicketTask(
            id="1",
            service_number=ServiceNumber("any_service_number"),
            auto_resolution_grace_period=timedelta(days=1),
            max_auto_resolutions=1,
            is_resolved=ANY,
            cycles=[],
        )
    }


@pytest.mark.parametrize(
    ["bruin_status", "is_task_resolved"],
    [
        ("R", True),
        ("any_status", False),
    ],
)
async def ticket_task_status_are_properly_built_test(bruin_status, is_task_resolved):
    # given
    ticket_detail = any_bruin_ticket_detail(detail_value="any_service_number", detail_status=bruin_status)
    bruin_ticket_data = BruinTicketData(ticketDetails=[ticket_detail])

    # when
    tasks = bruin_ticket_data.build_ticket_tasks_with(
        task_auto_resolution_grace_period=timedelta(days=1),
        task_max_auto_resolutions=1,
    )
    assert tasks == {
        "any_service_number": TicketTask(
            id=ANY,
            service_number=ANY,
            auto_resolution_grace_period=ANY,
            max_auto_resolutions=ANY,
            is_resolved=is_task_resolved,
            cycles=ANY,
        )
    }


# - varias notas manuales: cycles=[]
# - una nota triage-reopen: cycles=[ONGOING]
# - una nota triage-reopen y varias notas manuales: cycles=[ONGOING]
# - varias notas manuales y una nota triage-reopen: cycles=[ONGOING]
# - una nota auto-resolve: cycles=[AUTO_RESOLVE]
# - una nota auto-resolve y varias notas manuales: cycles=[AUTO_RESOLVE]
# - varias notas manuales y una nota auto-resolve: cycles=[AUTO_RESOLVE]
# - un par triage-reopen/autoresolve: cycles=[AUTO_RESOLVE]
# - dos pares de notas triage/reopen: cycles=[AUTO_RESOLVE, AUTO_RESOLVE]
# - un par triage-reopen/autoresolve y una nota auto-resolve: cycles=[AUTO_RESOLVE]
# - una nota triage-reopen, una nota manual y una nota auto-resolve: cycles=[AUTO_RESOLVE]
# - ¿algún test para probar la ordenación de las notas?
# - más combinaciones si hiciera falta
# Sacar todas las funciones de apoyo/shorthand necesarias para que el parametrize sea lo más legible posible
# Modificar la implementación del test si es necesario
@pytest.mark.skip
async def task_cycles_are_properly_built_test(bruin_ticket_notes: List[BruinTicketNote], expected_cycles):
    # given
    for bruin_ticket_note in bruin_ticket_notes:
        bruin_ticket_note.serviceNumber = ["any_service_number"]

    bruin_ticket_data = BruinTicketData(
        ticketDetails=[any_bruin_ticket_detail(detail_value="any_service_number")],
        ticketNotes=bruin_ticket_notes,
    )

    # when
    tasks = bruin_ticket_data.build_ticket_tasks_with(
        task_auto_resolution_grace_period=timedelta(days=1),
        task_max_auto_resolutions=1,
    )

    # then
    assert tasks.get(ServiceNumber("any_service_number")).cycles == expected_cycles


# - sin details y sin notes: tasks={}
# - 1 details y sin notes: tasks={Task(cycles=[])}
# - 1 details y con una nota triage de service number distinto: tasks={Task(cycles=[])}
# - 1 details y con una nota triage con mismo service number: tasks={Task(cycles=[ONGOING])}
# - 2 details y sin notes: tasks={Task(cycles=[]), Task(cycles=[])}
# - 2 details y dos notas triage de service number distinto: tasks={Task(cycles=[]), Task(cycles=[])}
# - 2 details y dos notas triage, una de ellas con mismo service number: tasks={Task(cycles=[ONGOING]), Task(cycles=[])}
# - 2 details y dos notas triage con mismo service number: tasks={Task(cycles=[ONGOING]), Task(cycles=[ONGOING])}
# - más combinaciones si hiciera falta
# Sacar todas las funciones de apoyo/shorthand necesarias para que el parametrize sea lo más legible posible
# Modificar la implementación del test si es necesario
@pytest.mark.skip
async def task_cycles_are_properly_detected_test(bruin_ticket_details, bruin_ticket_notes, expected_tasks):
    # given
    bruin_ticket_data = BruinTicketData(ticketDetails=bruin_ticket_details, ticketNotes=bruin_ticket_notes)

    # when
    tasks = bruin_ticket_data.build_ticket_tasks_with(
        task_auto_resolution_grace_period=timedelta(days=1),
        task_max_auto_resolutions=1,
    )

    # then
    assert tasks == expected_tasks


@pytest.fixture()
def any_valid_tickets_response():
    def builder(ticket_id: int = 1234, create_date: str = "10/10/2022 8:58:28 AM", created_by: str = "any_user"):
        response = {"responses": [{"ticketID": ticket_id, "createDate": create_date, "createdBy": created_by}]}
        return BruinResponse(status=200, text=json.dumps(response))

    return builder


@pytest.fixture()
def any_valid_ticket_data_response():
    def builder(ticket_id: int = 1234, create_date: str = "10/10/2022 8:58:28 AM", created_by: str = "any_user"):
        response = {"responses": [{"ticketID": ticket_id, "createDate": create_date, "createdBy": created_by}]}
        return BruinResponse(status=200, text=json.dumps(response))

    return builder


@pytest.fixture
def any_query(any_device_id):
    def builder(
        created_by: str = ANY,
        ticket_topic: str = ANY,
        device_id: DeviceId = any_device_id(),
        statuses: Optional[List[str]] = None,
    ):
        return FindTicketQuery(
            created_by=created_by, ticket_topic=ticket_topic, device_id=device_id, statuses=statuses or []
        )

    return builder


@pytest.fixture
def any_device_id():
    def builder(
        id: str = ANY,
        network_id: str = ANY,
        client_id: str = ANY,
        service_number: ServiceNumber = ANY,
        device_type: DeviceType = ANY,
    ):
        return DeviceId(
            id=id,
            network_id=network_id,
            client_id=client_id,
            service_number=service_number,
            type=device_type,
        )

    return builder
