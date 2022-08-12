from dataclasses import dataclass, field
from typing import Any, Dict, List

from application.domain.asset import Topic
from application.domain.repair_email_output import RepairEmailOutput, TicketOutput
from application.domain.ticket import Category, Ticket, TicketStatus
from application.rpc import RpcError
from application.rpc.upsert_outage_ticket_rpc import UpsertedStatus, UpsertedTicket


@dataclass
class RepairTicketsMonitorScenario:
    # Existing Bruin assets and their site
    assets: Dict[str, str] = field(default_factory=dict)

    # Existing Bruin tickets
    tickets: List["Ticket"] = field(default_factory=list)
    is_reply_email: bool = False

    # Integration behavior
    assets_actionable: bool = True
    tickets_actionable: bool = True
    # Bruin POST api/Ticket/repair responses
    upserted_tickets: Dict[str, UpsertedTicket] = field(default_factory=dict)
    # Bruin GET api/Ticket/topics mocks
    asset_topics: Dict[str, List[Topic]] = field(default_factory=dict)
    # append_note_to_ticket_rpc response
    append_note_to_ticket_effect: Any = lambda x, y: True
    # link_email_to_ticket response
    link_email_to_ticket_response: Any = field(default_factory=lambda: {"status": 200})

    # Expected behavior
    expected_output: RepairEmailOutput = None
    email_processed: bool = True
    autoreply_sent: bool = False
    parent_email_hidden: bool = False
    parent_email_unhidden: bool = False
    parent_email_saved: bool = False
    parent_email_removed: bool = False
    # Notes with service number added to a ticket (for asset processing)
    note_added_to: List[str] = field(default_factory=list)
    email_linked_to: List[str] = field(default_factory=list)
    # Notes without service number added to a ticket (for ticket processing)
    global_note_added_to: List[str] = field(default_factory=list)


class CreatedTicket(UpsertedTicket):
    status = UpsertedStatus.created


class UpdatedTicket(UpsertedTicket):
    status = UpsertedStatus.updated


def make_repair_tickets_monitor_scenarios():
    # Common values
    voo_topic = Topic(call_type="REP", category=Category.SERVICE_OUTAGE.value)
    wireless_topic = Topic(call_type="REP", category=Category.WIRELESS_SERVICE_NOT_WORKING.value)
    other_category_topic = Topic(call_type="REP", category="018")

    #
    # Empty emails
    #

    # check GetPrediction
    empty_reply_email = RepairTicketsMonitorScenario(
        assets={},
        tickets=[],
        is_reply_email=True,
        email_processed=False,
        parent_email_removed=True,
        parent_email_unhidden=True,
        expected_output=RepairEmailOutput(
            email_id="0",
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")],
        ),
    )

    empty_non_actionable_parent_email = RepairTicketsMonitorScenario(
        assets={},
        tickets=[],
        assets_actionable=False,
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")],
        ),
    )

    empty_actionable_parent_email = RepairTicketsMonitorScenario(
        assets={},
        tickets=[],
        email_processed=False,
        autoreply_sent=True,
        parent_email_saved=True,
        parent_email_hidden=True,
        expected_output=RepairEmailOutput(
            email_id="0",
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers. Sent auto-reply")],
        ),
    )

    #
    # Extracted Assets
    #

    single_unreported_asset = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        upserted_tickets={"asset_1": CreatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic]},
        note_added_to=["site_1_ticket"],
        email_linked_to=["site_1_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1"},
            tickets_created=[TicketOutput(ticket_id="site_1_ticket", site_id="site_1", service_numbers=["asset_1"])],
        ),
    )
    single_reported_asset = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        upserted_tickets={"asset_1": UpdatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic]},
        note_added_to=["site_1_ticket"],
        email_linked_to=["site_1_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1"},
            tickets_updated=[
                TicketOutput(
                    ticket_id="site_1_ticket",
                    site_id="site_1",
                    service_numbers=["asset_1"],
                    reason="update_with_asset_found",
                )
            ],
        ),
    )
    email_not_actionable_and_single_reported_asset = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        upserted_tickets={"asset_1": UpdatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic]},
        assets_actionable=False,
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1"},
            tickets_cannot_be_created=[
                TicketOutput(site_id="site_1", service_numbers=["asset_1"], reason="predicted class is Other")
            ],
        ),
    )
    several_related_unreported_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        upserted_tickets={"asset_1,asset_2": CreatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic], "asset_2": [voo_topic]},
        note_added_to=["site_1_ticket"],
        email_linked_to=["site_1_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_created=[
                TicketOutput(ticket_id="site_1_ticket", site_id="site_1", service_numbers=["asset_1", "asset_2"])
            ],
        ),
    )
    several_related_reported_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        upserted_tickets={"asset_1,asset_2": UpdatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic], "asset_2": [voo_topic]},
        note_added_to=["site_1_ticket"],
        email_linked_to=["site_1_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_updated=[
                TicketOutput(
                    ticket_id="site_1_ticket",
                    site_id="site_1",
                    service_numbers=["asset_1", "asset_2"],
                    reason="update_with_asset_found",
                )
            ],
        ),
    )
    several_unrelated_unreported_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_2"},
        upserted_tickets={
            "asset_1": CreatedTicket(ticket_id="site_1_ticket"),
            "asset_2": CreatedTicket(ticket_id="site_2_ticket"),
        },
        asset_topics={"asset_1": [voo_topic], "asset_2": [voo_topic]},
        note_added_to=["site_1_ticket", "site_2_ticket"],
        email_linked_to=["site_1_ticket", "site_2_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_2"},
            tickets_created=[
                TicketOutput(ticket_id="site_1_ticket", site_id="site_1", service_numbers=["asset_1"]),
                TicketOutput(ticket_id="site_2_ticket", site_id="site_2", service_numbers=["asset_2"]),
            ],
        ),
    )
    several_unrelated_reported_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_2"},
        upserted_tickets={
            "asset_1": UpdatedTicket(ticket_id="site_1_ticket"),
            "asset_2": UpdatedTicket(ticket_id="site_2_ticket"),
        },
        asset_topics={"asset_1": [voo_topic], "asset_2": [voo_topic]},
        note_added_to=["site_1_ticket", "site_2_ticket"],
        email_linked_to=["site_1_ticket", "site_2_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_2"},
            tickets_updated=[
                TicketOutput(
                    ticket_id="site_1_ticket",
                    site_id="site_1",
                    service_numbers=["asset_1"],
                    reason="update_with_asset_found",
                ),
                TicketOutput(
                    ticket_id="site_2_ticket",
                    site_id="site_2",
                    service_numbers=["asset_2"],
                    reason="update_with_asset_found",
                ),
            ],
        ),
    )

    #
    # Asset topics
    #

    single_no_topics_asset = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        asset_topics={"asset_1": []},
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1"},
            tickets_cannot_be_created=[TicketOutput(reason="no_topics_detected")],
        ),
    )
    single_wireless_asset = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        asset_topics={"asset_1": [wireless_topic]},
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1"},
            tickets_cannot_be_created=[TicketOutput(reason="contains_wireless_assets")],
        ),
    )
    single_other_category_asset = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        asset_topics={"asset_1": [other_category_topic]},
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1"},
            tickets_cannot_be_created=[TicketOutput(reason="contains_other_assets")],
        ),
    )
    several_wireless_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        asset_topics={"asset_1": [wireless_topic], "asset_2": [wireless_topic]},
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_cannot_be_created=[TicketOutput(reason="contains_wireless_assets")],
        ),
    )
    several_other_category_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        asset_topics={"asset_1": [other_category_topic], "asset_2": [other_category_topic]},
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_cannot_be_created=[TicketOutput(reason="contains_other_assets")],
        ),
    )
    wireless_and_no_topic_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        asset_topics={"asset_1": [wireless_topic], "asset_2": []},
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_cannot_be_created=[TicketOutput(reason="contains_wireless_assets")],
        ),
    )
    wireless_and_other_category_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        asset_topics={"asset_1": [wireless_topic], "asset_2": [other_category_topic]},
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_cannot_be_created=[TicketOutput(reason="contains_wireless_assets")],
        ),
    )
    voo_and_wireless_category_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        upserted_tickets={"asset_1": CreatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic], "asset_2": [wireless_topic]},
        email_processed=False,
        note_added_to=["site_1_ticket"],
        email_linked_to=["site_1_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_created=[TicketOutput(ticket_id="site_1_ticket", site_id="site_1", service_numbers=["asset_1"])],
            tickets_cannot_be_created=[TicketOutput(reason="contains_wireless_assets")],
        ),
    )
    voo_and_other_category_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        upserted_tickets={"asset_1": CreatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic], "asset_2": [other_category_topic]},
        email_processed=False,
        note_added_to=["site_1_ticket"],
        email_linked_to=["site_1_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_created=[TicketOutput(ticket_id="site_1_ticket", site_id="site_1", service_numbers=["asset_1"])],
            tickets_cannot_be_created=[TicketOutput(reason="contains_other_assets")],
        ),
    )
    voo_wireless_and_other_category_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1", "asset_3": "site_1"},
        upserted_tickets={"asset_1": UpdatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic], "asset_2": [wireless_topic], "asset_3": [other_category_topic]},
        email_processed=False,
        note_added_to=["site_1_ticket"],
        email_linked_to=["site_1_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1", "asset_3": "site_1"},
            tickets_updated=[
                TicketOutput(
                    ticket_id="site_1_ticket",
                    site_id="site_1",
                    service_numbers=["asset_1"],
                    reason="update_with_asset_found",
                )
            ],
            tickets_cannot_be_created=[TicketOutput(reason="contains_wireless_assets")],
        ),
    )
    several_sites_mixed_category_assets = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_2", "asset_3": "site_2"},
        asset_topics={"asset_1": [other_category_topic], "asset_2": [wireless_topic], "asset_3": [voo_topic]},
        upserted_tickets={"asset_3": CreatedTicket(ticket_id="site_2_ticket")},
        email_processed=False,
        note_added_to=["site_2_ticket"],
        email_linked_to=["site_2_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_2", "asset_3": "site_2"},
            tickets_created=[TicketOutput(ticket_id="site_2_ticket", site_id="site_2", service_numbers=["asset_3"])],
            tickets_cannot_be_created=[TicketOutput(reason="contains_wireless_assets")],
        ),
    )

    #
    # Extracted Tickets
    #

    single_operable_ticket = RepairTicketsMonitorScenario(
        tickets=[Ticket("ticket_1", status=TicketStatus.NEW, call_type="REP", category="VOO")],
        global_note_added_to=["ticket_1"],
        email_linked_to=["ticket_1"],
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[Ticket("ticket_1", status=TicketStatus.NEW, call_type="REP", category="VOO")],
            tickets_updated=[TicketOutput(ticket_id="ticket_1", reason="update_with_ticket_found")],
        ),
    )
    single_inoperable_ticket = RepairTicketsMonitorScenario(
        tickets=[Ticket("ticket_1", status=TicketStatus.DRAFT)],
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[Ticket("ticket_1", status=TicketStatus.DRAFT)],
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")],
        ),
    )
    multiple_operable_tickets = RepairTicketsMonitorScenario(
        tickets=[
            Ticket("ticket_1", status=TicketStatus.NEW, category="VOO"),
            Ticket("ticket_2", status=TicketStatus.IN_PROGRESS, category="VAS"),
        ],
        global_note_added_to=["ticket_1", "ticket_2"],
        email_linked_to=["ticket_1", "ticket_2"],
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[
                Ticket("ticket_1", status=TicketStatus.NEW, category="VOO"),
                Ticket("ticket_2", status=TicketStatus.IN_PROGRESS, category="VAS"),
            ],
            tickets_updated=[
                TicketOutput(ticket_id="ticket_1", reason="update_with_ticket_found"),
                TicketOutput(ticket_id="ticket_2", reason="update_with_ticket_found"),
            ],
        ),
    )
    multiple_inoperable_tickets = RepairTicketsMonitorScenario(
        tickets=[
            Ticket("ticket_1", status=TicketStatus.NEW, category="019"),
            Ticket("ticket_2", status=TicketStatus.DRAFT, category="VOO"),
        ],
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[
                Ticket("ticket_1", status=TicketStatus.NEW, category="019"),
                Ticket("ticket_2", status=TicketStatus.DRAFT, category="VOO"),
            ],
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")],
        ),
    )
    multiple_mixed_operability_tickets = RepairTicketsMonitorScenario(
        tickets=[
            Ticket("ticket_1", status=TicketStatus.NEW, call_type="REP", category="VOO"),
            Ticket("ticket_2", status=TicketStatus.DRAFT),
        ],
        global_note_added_to=["ticket_1"],
        email_linked_to=["ticket_1"],
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[
                Ticket("ticket_1", status=TicketStatus.NEW, call_type="REP", category="VOO"),
                Ticket("ticket_2", status=TicketStatus.DRAFT),
            ],
            tickets_updated=[TicketOutput(ticket_id="ticket_1", reason="update_with_ticket_found")],
        ),
    )
    append_global_note_not_ok = RepairTicketsMonitorScenario(
        tickets=[Ticket("ticket_1", status=TicketStatus.NEW, category="VOO")],
        email_processed=False,
        global_note_added_to=["ticket_1"],
        append_note_to_ticket_effect=lambda x, y: False,
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[Ticket("ticket_1", status=TicketStatus.NEW, category="VOO")],
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")],
        ),
    )
    append_global_note_error = RepairTicketsMonitorScenario(
        tickets=[Ticket("ticket_1", status=TicketStatus.NEW, category="VOO")],
        email_processed=False,
        global_note_added_to=["ticket_1"],
        append_note_to_ticket_effect=RpcError,
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[Ticket("ticket_1", status=TicketStatus.NEW, category="VOO")],
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")],
        ),
    )
    link_email_not_ok = RepairTicketsMonitorScenario(
        tickets=[Ticket("ticket_1", status=TicketStatus.NEW, category="VOO")],
        email_processed=False,
        link_email_to_ticket_response={"status": 400},
        global_note_added_to=["ticket_1"],
        email_linked_to=["ticket_1"],
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[Ticket("ticket_1", status=TicketStatus.NEW, category="VOO")],
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")],
        ),
    )
    email_not_actionable_and_single_operable_ticket = RepairTicketsMonitorScenario(
        tickets=[Ticket("ticket_1", status=TicketStatus.NEW, call_type="REP", category="VOO")],
        tickets_actionable=False,
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id="0",
            validated_tickets=[Ticket("ticket_1", status=TicketStatus.NEW, call_type="REP", category="VOO")],
            tickets_could_be_updated=[TicketOutput(ticket_id="ticket_1")],
        ),
    )
    single_reported_asset_single_operable_ticket = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        tickets=[Ticket("ticket_1", status=TicketStatus.NEW, call_type="REP", category="VOO")],
        upserted_tickets={"asset_1": CreatedTicket(ticket_id="site_1_ticket")},
        asset_topics={"asset_1": [voo_topic]},
        note_added_to=["site_1_ticket"],
        email_linked_to=["site_1_ticket"],
        global_note_added_to=[],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1"},
            validated_tickets=[Ticket("ticket_1", status=TicketStatus.NEW, call_type="REP", category="VOO")],
            tickets_created=[TicketOutput(ticket_id="site_1_ticket", site_id="site_1", service_numbers=["asset_1"])],
        ),
    )
    single_no_voo_asset_single_operable_ticket = RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        tickets=[Ticket("site_1_ticket", status=TicketStatus.NEW, call_type="REP", category="VOO")],
        asset_topics={"asset_1": [wireless_topic]},
        email_processed=False,
        email_linked_to=["site_1_ticket"],
        global_note_added_to=["site_1_ticket"],
        expected_output=RepairEmailOutput(
            email_id="0",
            service_numbers_sites_map={"asset_1": "site_1"},
            validated_tickets=[Ticket("site_1_ticket", status=TicketStatus.NEW, call_type="REP", category="VOO")],
            tickets_updated=[TicketOutput(ticket_id="site_1_ticket", reason="update_with_ticket_found")],
            tickets_cannot_be_created=[TicketOutput(reason="contains_wireless_assets")],
        ),
    )

    return {
        # Empty emails
        "empty_reply_email": empty_reply_email,
        # "empty_actionable_parent_email": empty_actionable_parent_email,
        "empty_non_actionable_parent_email": empty_non_actionable_parent_email,
        # Assets
        "single_unreported_asset": single_unreported_asset,
        "single_reported_asset": single_reported_asset,
        "email_not_actionable_and_single_reported_asset": email_not_actionable_and_single_reported_asset,
        "several_related_unreported_assets": several_related_unreported_assets,
        "several_related_reported_assets": several_related_reported_assets,
        "several_unrelated_unreported_assets": several_unrelated_unreported_assets,
        "several_unrelated_reported_assets": several_unrelated_reported_assets,
        # Asset topics
        "single_no_topics_asset": single_no_topics_asset,
        "single_wireless_asset": single_wireless_asset,
        "single_other_category_asset": single_other_category_asset,
        "several_wireless_assets": several_wireless_assets,
        "several_other_category_assets": several_other_category_assets,
        "wireless_and_no_topic_assets": wireless_and_no_topic_assets,
        "wireless_and_other_category_assets": wireless_and_other_category_assets,
        "voo_and_wireless_category_assets": voo_and_wireless_category_assets,
        "voo_and_other_category_assets": voo_and_other_category_assets,
        "voo_wireless_and_other_category_assets": voo_wireless_and_other_category_assets,
        "several_sites_mixed_category_assets": several_sites_mixed_category_assets,
        # Tickets
        "single_operable_ticket": single_operable_ticket,
        "single_inoperable_ticket": single_inoperable_ticket,
        "multiple_operable_tickets": multiple_operable_tickets,
        "multiple_inoperable_tickets": multiple_inoperable_tickets,
        "multiple_mixed_operability_tickets": multiple_mixed_operability_tickets,
        "append_global_note_not_ok": append_global_note_not_ok,
        "append_global_note_error": append_global_note_error,
        "link_email_not_ok": link_email_not_ok,
        "email_not_actionable_and_single_operable_ticket": email_not_actionable_and_single_operable_ticket,
        "single_reported_asset_single_operable_ticket": single_reported_asset_single_operable_ticket,
        "single_no_voo_asset_single_operable_ticket": single_no_voo_asset_single_operable_ticket,
    }
