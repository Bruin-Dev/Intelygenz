from http import HTTPStatus
from typing import List
from unittest.mock import ANY, AsyncMock, Mock

from application import resources
from application.actions.repair_tickets_monitor import RepairTicketsMonitor
from application.domain.asset import AssetId
from application.domain.email import EmailStatus
from application.rpc import RpcFailedError, RpcRequest, RpcResponse
from config import testconfig as config
from pytest import fixture, mark
from tests.actions.repair_tickets_monitor_scenarios import (
    RepairTicketsMonitorScenario,
    make_repair_tickets_monitor_scenarios,
)
from tests.fixtures.domain import AnyEmail

scenarios = make_repair_tickets_monitor_scenarios()


@mark.asyncio
@mark.parametrize("scenario", scenarios.values(), ids=list(scenarios.keys()))
async def repair_tickets_monitor_scenarios_test(
    scenario: RepairTicketsMonitorScenario,
    repair_tickets_monitor,
    repair_ticket_kre_repository,
    bruin_repository,
    inference_data_for,
):
    def get_asset_topics_effect(asset_id: AssetId):
        return scenario.asset_topics.get(asset_id.service_number, [])

    def upsert_outage_ticket_rpc(asset_ids: List[AssetId], contact_email: str):
        service_numbers = ",".join([asset_id.service_number for asset_id in asset_ids])
        upsert_result = scenario.upserted_tickets.get(service_numbers)
        if upsert_result:
            return upsert_result
        else:
            raise RpcFailedError(request=RpcRequest.construct(), response=RpcResponse(status=HTTPStatus.BAD_REQUEST))

    repair_tickets_monitor._append_note_to_ticket_rpc = AsyncMock(side_effect=scenario.append_note_to_ticket_effect)
    repair_tickets_monitor._get_asset_topics_rpc = AsyncMock(side_effect=get_asset_topics_effect)
    repair_tickets_monitor._upsert_outage_ticket_rpc = AsyncMock(side_effect=upsert_outage_ticket_rpc)
    repair_tickets_monitor._set_email_status_rpc = AsyncMock()
    repair_tickets_monitor._send_email_reply_rpc = AsyncMock()
    repair_tickets_monitor._new_tagged_emails_repository.save_parent_email = Mock()
    repair_tickets_monitor._new_tagged_emails_repository.remove_parent_email = Mock()
    repair_ticket_kre_repository.get_email_inference = AsyncMock(return_value=inference_data_for(scenario))
    mock_bruin_repository(bruin_repository, scenario)

    email = AnyEmail(id="0")
    if scenario.is_reply_email:
        email.parent = AnyEmail(id="1")

    await repair_tickets_monitor._process_repair_email(email)

    if scenario.expected_output is None:
        repair_ticket_kre_repository.save_outputs.assert_not_awaited()
    else:
        repair_ticket_kre_repository.save_outputs.assert_awaited_once_with(scenario.expected_output)

    if scenario.email_processed:
        bruin_repository.mark_email_as_done.assert_awaited_once()
    else:
        bruin_repository.mark_email_as_done.assert_not_awaited()

    if scenario.parent_email_hidden:
        repair_tickets_monitor._set_email_status_rpc.assert_awaited_once_with(email.id, EmailStatus.AIQ)

    if scenario.parent_email_unhidden:
        repair_tickets_monitor._set_email_status_rpc.assert_awaited_once_with(email.parent.id, EmailStatus.NEW)

    if scenario.autoreply_sent:
        repair_tickets_monitor._send_email_reply_rpc.assert_awaited_once_with(email.id, resources.AUTO_REPLY_BODY)
    else:
        repair_tickets_monitor._send_email_reply_rpc.assert_not_awaited()

    if scenario.parent_email_saved:
        repair_tickets_monitor._new_tagged_emails_repository.save_parent_email.assert_called_once_with(email)
    else:
        repair_tickets_monitor._new_tagged_emails_repository.save_parent_email.assert_not_called()

    if scenario.parent_email_removed:
        repair_tickets_monitor._new_tagged_emails_repository.remove_parent_email.assert_called_once_with(email.parent)
    else:
        repair_tickets_monitor._new_tagged_emails_repository.remove_parent_email.assert_not_called()

    assert bruin_repository.append_notes_to_ticket.await_count == len(scenario.note_added_to)
    for ticket_id in scenario.note_added_to:
        bruin_repository.append_notes_to_ticket.assert_any_await(ticket_id, ANY)

    assert bruin_repository.link_email_to_ticket.await_count == len(scenario.email_linked_to)
    for ticket_id in scenario.email_linked_to:
        bruin_repository.link_email_to_ticket.assert_any_await(ticket_id, ANY)

    assert repair_tickets_monitor._append_note_to_ticket_rpc.await_count == len(scenario.global_note_added_to)
    for ticket_id in scenario.global_note_added_to:
        repair_tickets_monitor._append_note_to_ticket_rpc.assert_any_await(ticket_id, ANY)


@fixture
def inference_data_for(make_inference_data, make_filter_flags):
    def builder(scenario: RepairTicketsMonitorScenario):
        return {
            "status": 200,
            "body": make_inference_data(
                potential_service_numbers=list(scenario.assets.keys()),
                potential_tickets_numbers=[ticket.id for ticket in scenario.tickets],
                predicted_class="" if scenario.assets_actionable else "Other",
                filter_flags=make_filter_flags(
                    is_filtered=False if scenario.tickets_actionable else True,
                ),
            ),
        }

    return builder


@fixture(scope="function")
def repair_tickets_monitor(
    event_bus,
    scheduler,
    bruin_repository,
    new_tagged_emails_repository,
    repair_ticket_kre_repository,
    make_email,
    make_inference_data,
) -> RepairTicketsMonitor:
    new_tagged_emails_repository.get_email_details = Mock(return_value=make_email())
    repair_ticket_kre_repository.save_outputs = AsyncMock()

    return RepairTicketsMonitor(
        event_bus,
        scheduler,
        config,
        bruin_repository,
        new_tagged_emails_repository,
        repair_ticket_kre_repository,
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
    )


def mock_bruin_repository(bruin_repository, scenario: RepairTicketsMonitorScenario):
    def verify_service_number_information(_, potential_service_number: str):
        return {"status": 200, "body": {"site_id": scenario.assets.get(potential_service_number, 0)}}

    def get_single_ticket_basic_info(ticket_id: str):
        ticket_map = dict((ticket.id, ticket) for ticket in scenario.tickets)
        ticket = ticket_map.get(ticket_id)
        if ticket:
            return {
                "status": 200,
                "body": {
                    "ticket_id": ticket.id,
                    "ticket_status": ticket.status.value,
                    "call_type": ticket.call_type,
                    "category": ticket.category,
                },
            }
        else:
            return {"status": 400}

    bruin_repository.verify_service_number_information = AsyncMock(side_effect=verify_service_number_information)
    bruin_repository.get_single_ticket_basic_info = AsyncMock(side_effect=get_single_ticket_basic_info)
    bruin_repository.get_existing_tickets_with_service_numbers = AsyncMock(return_value={"status": 200, "body": []})
    bruin_repository.link_email_to_ticket = AsyncMock(return_value=scenario.link_email_to_ticket_response)
