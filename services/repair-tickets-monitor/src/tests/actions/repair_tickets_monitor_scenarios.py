from typing import Dict, List

from dataclasses import dataclass, field

from application.domain.repair_email_output import RepairEmailOutput, TicketOutput
from application.domain.ticket import Ticket, TicketStatus


@dataclass
class RepairTicketsMonitorScenario:
    # Existing Bruin assets and their site
    assets: Dict[str, str] = field(default_factory=dict)
    # Bruin POST api/Ticker/repair responses
    post_responses: Dict[str, 'PostResponse'] = field(default_factory=dict)

    # Existing Bruin tickets
    tickets: List['Ticket'] = field(default_factory=list)

    # Expected behavior
    expected_output: RepairEmailOutput = None
    email_processed: bool = True
    # Notes with service number added to a ticket (for asset processing)
    note_added_to: List[int] = field(default_factory=list)
    email_linked_to: List[int] = field(default_factory=list)
    # Notes without service number added to a ticket (for ticket processing)
    global_note_added_to: List[int] = field(default_factory=list)


@dataclass
class PostResponse:
    status: int
    body: int


@dataclass
class CreatedResponse(PostResponse):
    status: int = field(init=False, default=200)


@dataclass
class UpdatedResponse(PostResponse):
    status: int = field(init=False, default=409)


# @dataclass
# class ErrorResponse(PostResponse):
#     status: int = field(init=False, default=500)


def make_repair_tickets_monitor_scenarios():
    no_assets_and_no_tickets = RepairTicketsMonitorScenario(
        assets={},
        tickets=[],
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id=0,
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")]
        ),
    )

    #
    # Extracted Assets
    #
    single_unreported_asset = (RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        post_responses={"asset_1": CreatedResponse(hash("site_1_ticket"))},
        email_processed=True,
        note_added_to=[hash("site_1_ticket")],
        email_linked_to=[hash("site_1_ticket")],
        expected_output=RepairEmailOutput(
            email_id=0,
            service_numbers_sites_map={"asset_1": "site_1"},
            tickets_created=[TicketOutput(
                ticket_id=hash("site_1_ticket"),
                site_id="site_1",
                service_numbers=["asset_1"]
            )]
        )
    ))
    single_reported_asset = (RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1"},
        post_responses={"asset_1": UpdatedResponse(hash("site_1_ticket"))},
        email_processed=True,
        note_added_to=[hash("site_1_ticket")],
        email_linked_to=[hash("site_1_ticket")],
        expected_output=RepairEmailOutput(
            email_id=0,
            service_numbers_sites_map={"asset_1": "site_1"},
            tickets_updated=[TicketOutput(
                ticket_id=hash("site_1_ticket"),
                site_id="site_1",
                service_numbers=["asset_1"],
                reason="update_with_asset_found"
            )]
        )
    ))
    several_related_unreported_assets = (RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        post_responses={"asset_1,asset_2": CreatedResponse(hash("site_1_ticket"))},
        email_processed=True,
        note_added_to=[hash("site_1_ticket")],
        email_linked_to=[hash("site_1_ticket")],
        expected_output=RepairEmailOutput(
            email_id=0,
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_created=[TicketOutput(
                ticket_id=hash("site_1_ticket"),
                site_id="site_1",
                service_numbers=["asset_1", "asset_2"]
            )]
        )
    ))
    several_related_reported_assets = (RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_1"},
        post_responses={"asset_1,asset_2": UpdatedResponse(hash("site_1_ticket"))},
        email_processed=True,
        note_added_to=[hash("site_1_ticket")],
        email_linked_to=[hash("site_1_ticket")],
        expected_output=RepairEmailOutput(
            email_id=0,
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_1"},
            tickets_updated=[TicketOutput(
                ticket_id=hash("site_1_ticket"),
                site_id="site_1",
                service_numbers=["asset_1", "asset_2"],
                reason="update_with_asset_found"
            )]
        )
    ))
    several_unrelated_unreported_assets = (RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_2"},
        post_responses={
            "asset_1": CreatedResponse(hash("site_1_ticket")),
            "asset_2": CreatedResponse(hash("site_2_ticket")),
        },
        email_processed=True,
        note_added_to=[hash("site_1_ticket"), hash("site_2_ticket")],
        email_linked_to=[hash("site_1_ticket"), hash("site_2_ticket")],
        expected_output=RepairEmailOutput(
            email_id=0,
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_2"},
            tickets_created=[
                TicketOutput(
                    ticket_id=hash("site_1_ticket"),
                    site_id="site_1",
                    service_numbers=["asset_1"]
                ),
                TicketOutput(
                    ticket_id=hash("site_2_ticket"),
                    site_id="site_2",
                    service_numbers=["asset_2"]
                ),
            ]
        )
    ))
    several_unrelated_reported_assets = (RepairTicketsMonitorScenario(
        assets={"asset_1": "site_1", "asset_2": "site_2"},
        post_responses={
            "asset_1": UpdatedResponse(hash("site_1_ticket")),
            "asset_2": UpdatedResponse(hash("site_2_ticket")),
        },
        email_processed=True,
        note_added_to=[hash("site_1_ticket"), hash("site_2_ticket")],
        email_linked_to=[hash("site_1_ticket"), hash("site_2_ticket")],
        expected_output=RepairEmailOutput(
            email_id=0,
            service_numbers_sites_map={"asset_1": "site_1", "asset_2": "site_2"},
            tickets_updated=[
                TicketOutput(
                    ticket_id=hash("site_1_ticket"),
                    site_id="site_1",
                    service_numbers=["asset_1"],
                    reason="update_with_asset_found"
                ),
                TicketOutput(
                    ticket_id=hash("site_2_ticket"),
                    site_id="site_2",
                    service_numbers=["asset_2"],
                    reason="update_with_asset_found"
                ),
            ]
        )
    ))

    #
    # Extracted Tickets
    #

    single_operable_ticket = (RepairTicketsMonitorScenario(
        tickets=[Ticket(hash("ticket_1"), status=TicketStatus.NEW, call_type="REP", category="VOO")],
        global_note_added_to=[hash("ticket_1")],
        email_linked_to=[hash("ticket_1")],
        expected_output=RepairEmailOutput(
            email_id=0,
            validated_tickets=[
                Ticket(hash("ticket_1"), status=TicketStatus.NEW, call_type="REP", category="VOO"),
            ],
            tickets_updated=[TicketOutput(ticket_id=hash("ticket_1"), reason="update_with_ticket_found")]
        )
    ))
    single_inoperable_ticket = (RepairTicketsMonitorScenario(
        tickets=[Ticket(hash("ticket_1"), status=TicketStatus.DRAFT)],
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id=0,
            validated_tickets=[
                Ticket(hash("ticket_1"), status=TicketStatus.DRAFT),
            ],
            tickets_cannot_be_created=[TicketOutput(
                reason="No validated service numbers"
            )]
        )
    ))
    multiple_operable_tickets = (RepairTicketsMonitorScenario(
        tickets=[
            Ticket(hash("ticket_1"), status=TicketStatus.NEW, category="VOO"),
            Ticket(hash("ticket_2"), status=TicketStatus.IN_PROGRESS, category="VAS")
        ],
        global_note_added_to=[hash("ticket_1"), hash("ticket_2")],
        email_linked_to=[hash("ticket_1"), hash("ticket_2")],
        expected_output=RepairEmailOutput(
            email_id=0,
            validated_tickets=[
                Ticket(hash("ticket_1"), status=TicketStatus.NEW, category="VOO"),
                Ticket(hash("ticket_2"), status=TicketStatus.IN_PROGRESS, category="VAS")
            ],
            tickets_updated=[TicketOutput(
                ticket_id=hash("ticket_1"),
                reason="update_with_ticket_found"
            ), TicketOutput(
                ticket_id=hash("ticket_2"),
                reason="update_with_ticket_found"
            )]
        )
    ))
    multiple_inoperable_tickets = (RepairTicketsMonitorScenario(
        tickets=[
            Ticket(hash("ticket_1"), status=TicketStatus.NEW, category="019"),
            Ticket(hash("ticket_2"), status=TicketStatus.DRAFT, category="VOO")
        ],
        email_processed=False,
        expected_output=RepairEmailOutput(
            email_id=0,
            validated_tickets=[
                Ticket(hash("ticket_1"), status=TicketStatus.NEW, category="019"),
                Ticket(hash("ticket_2"), status=TicketStatus.DRAFT, category="VOO")
            ],
            tickets_cannot_be_created=[TicketOutput(reason="No validated service numbers")]
        )
    ))
    multiple_mixed_operability_tickets = (RepairTicketsMonitorScenario(
        tickets=[
            Ticket(hash("ticket_1"), status=TicketStatus.NEW, call_type="REP", category="VOO"),
            Ticket(hash("ticket_2"), status=TicketStatus.DRAFT)
        ],
        global_note_added_to=[hash("ticket_1")],
        email_linked_to=[hash("ticket_1")],
        expected_output=RepairEmailOutput(
            email_id=0,
            validated_tickets=[
                Ticket(hash("ticket_1"), status=TicketStatus.NEW, call_type="REP", category="VOO"),
                Ticket(hash("ticket_2"), status=TicketStatus.DRAFT)
            ],
            tickets_updated=[TicketOutput(
                ticket_id=hash("ticket_1"),
                reason="update_with_ticket_found"
            )],
        )
    ))

    return {
        "no_assets_and_no_tickets": no_assets_and_no_tickets,
        "single_unreported_asset": single_unreported_asset,
        "single_reported_asset": single_reported_asset,
        "several_related_unreported_assets": several_related_unreported_assets,
        "several_related_reported_assets": several_related_reported_assets,
        "several_unrelated_unreported_assets": several_unrelated_unreported_assets,
        "several_unrelated_reported_assets": several_unrelated_reported_assets,
        "single_operable_ticket": single_operable_ticket,
        "single_inoperable_ticket": single_inoperable_ticket,
        "multiple_operable_tickets": multiple_operable_tickets,
        "multiple_inoperable_tickets": multiple_inoperable_tickets,
        "multiple_mixed_operability_tickets": multiple_mixed_operability_tickets,
    }
