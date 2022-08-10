import logging

from application.data.bruin.ticket_basic import Response, TicketBasic
from application.data.bruin.ticket_details import TicketDetails
from application.handler import WillExecute, WillReturnJSON
from application.scenario import Scenario
from application.servers.grpc.rta.rta import RtaService
from dataclasses import dataclass
from starlette.requests import Request
from starlette.responses import JSONResponse

log = logging.getLogger(__name__)


@dataclass
class ClosedTicketsFeedback(Scenario):
    name: str = "Closed tickets feedback"

    async def run(self):
        # given ...
        # - Bruin has a closed ticket
        ticket_number = hash("any_ticket_number")
        single_ticket = TicketBasic(total=1, responses=[Response(ticketID=ticket_number, createdBy="Intelygenz Ai")])

        async def closed_ticket(request: Request):
            query_closed = request.query_params.get("TicketStatus") == "Closed"
            query_voo = request.query_params.get("TicketTopic") == "VOO"
            if query_closed and query_voo:
                return JSONResponse(single_ticket.dict())
            else:
                return JSONResponse(TicketBasic().dict())

        self.given("/api/Ticket/basic", WillExecute(closed_ticket))

        # - Bruin will return the details of the ticket
        self.given(f"/api/Ticket/{ticket_number}/details", WillReturnJSON(TicketDetails()))

        # when
        # RTA polls for closed tickets

        # then
        from application.scenarios import timeout

        return await self.check(
            # [rta] konstellation was sent the result of RTA
            self.route(RtaService.path("SaveClosedTicketsFeedback")).was_reached(timeout.STANDALONE_RTA),
        )


rta_poll_scenarios = [
    ClosedTicketsFeedback(),
]
