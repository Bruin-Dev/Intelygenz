from typing import List
from unittest.mock import Mock, ANY

from asynctest import CoroutineMock
from dataclasses import asdict
from pytest import mark, fixture

from application.actions.repair_tickets_monitor import RepairTicketsMonitor
from config import testconfig as config
from tests.actions.repair_tickets_monitor_scenarios import RepairTicketsMonitorScenario, PostResponse, \
    make_repair_tickets_monitor_scenarios

scenarios = make_repair_tickets_monitor_scenarios()


@mark.asyncio
@mark.parametrize("scenario", scenarios.values(), ids=list(scenarios.keys()))
async def repair_tickets_monitor_scenarios_test(
    scenario: RepairTicketsMonitorScenario,
    repair_tickets_monitor,
    repair_ticket_kre_repository,
    bruin_repository,
    inference_data_for,
    make_email_tag_info,
):
    repair_tickets_monitor.append_note_to_ticket_rpc = CoroutineMock(side_effect=scenario.append_note_to_ticket_effect)
    repair_ticket_kre_repository.get_email_inference = CoroutineMock(return_value=inference_data_for(scenario))
    mock_bruin_repository(bruin_repository, scenario)

    await repair_tickets_monitor._process_repair_email(make_email_tag_info())

    if scenario.expected_output is None:
        repair_ticket_kre_repository.save_outputs.assert_not_awaited()
    else:
        repair_ticket_kre_repository.save_outputs.assert_awaited_once_with(scenario.expected_output)

    if scenario.email_processed:
        bruin_repository.mark_email_as_done.assert_awaited_once()
    else:
        bruin_repository.mark_email_as_done.assert_not_awaited()

    assert bruin_repository.append_notes_to_ticket.await_count == len(scenario.note_added_to)
    for ticket_id in scenario.note_added_to:
        bruin_repository.append_notes_to_ticket.assert_any_await(ticket_id, ANY)

    assert bruin_repository.link_email_to_ticket.await_count == len(scenario.email_linked_to)
    for ticket_id in scenario.email_linked_to:
        bruin_repository.link_email_to_ticket.assert_any_await(ticket_id, ANY)

    assert repair_tickets_monitor.append_note_to_ticket_rpc.await_count == len(scenario.global_note_added_to)
    for ticket_id in scenario.global_note_added_to:
        repair_tickets_monitor.append_note_to_ticket_rpc.assert_any_await(ticket_id, ANY)


@fixture
def inference_data_for(make_inference_data):
    def builder(scenario: RepairTicketsMonitorScenario):
        return {
            "status": 200,
            "body": make_inference_data(
                potential_service_numbers=list(scenario.assets.keys()),
                potential_tickets_numbers=[ticket.id for ticket in scenario.tickets],
                predicted_class="" if scenario.email_actionable else "Other"
            )
        }

    return builder


@fixture(scope='function')
def repair_tickets_monitor(
    event_bus,
    logger,
    scheduler,
    bruin_repository,
    new_tagged_emails_repository,
    repair_ticket_kre_repository,
    make_email,
    make_inference_data,
) -> RepairTicketsMonitor:
    new_tagged_emails_repository.get_email_details = Mock(return_value=make_email())
    repair_ticket_kre_repository.save_outputs = CoroutineMock()

    return RepairTicketsMonitor(
        event_bus,
        logger,
        scheduler,
        config,
        bruin_repository,
        new_tagged_emails_repository,
        repair_ticket_kre_repository,
        CoroutineMock()
    )


def mock_bruin_repository(bruin_repository, scenario: RepairTicketsMonitorScenario):
    def verify_service_number_information(_, potential_service_number: str):
        return {"status": 200, "body": {"site_id": scenario.assets.get(potential_service_number, 0)}}

    def create_outage_ticket(_, service_numbers: List[str], __):
        default_response = PostResponse(404, hash("created_ticket_id"))
        return asdict(scenario.post_responses.get(",".join(service_numbers), default_response))

    def get_single_ticket_basic_info(ticket_id: int):
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
                }
            }
        else:
            return {"status": 400}

    bruin_repository.verify_service_number_information = CoroutineMock(
        side_effect=verify_service_number_information
    )
    bruin_repository.create_outage_ticket = CoroutineMock(
        side_effect=create_outage_ticket
    )
    bruin_repository.get_single_ticket_basic_info = CoroutineMock(
        side_effect=get_single_ticket_basic_info
    )
    bruin_repository.get_existing_tickets_with_service_numbers = CoroutineMock(
        return_value={"status": 200, "body": []}
    )
    bruin_repository.link_email_to_ticket = CoroutineMock(return_value=scenario.link_email_to_ticket_response)