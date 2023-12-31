import logging
from dataclasses import dataclass

from application.clients import bruin
from application.data.bruin import Document, Email, Inventory, TicketModel
from application.data.bruin.ticket_basic import Response, TicketBasic
from application.data.bruin.ticket_details import TicketDetails, TicketNote
from application.data.bruin.ticket_repair import Item, TicketRepair
from application.data.bruin.ticket_topics import CallType, TicketTopics
from application.data.email_tagger import prediction
from application.handler import WillExecute, WillReturn, WillReturnJSON
from application.scenario import Scenario, ScenarioResult
from application.scenarios import timeout
from application.servers.grpc.email_tagger import email_tagger
from application.servers.grpc.email_tagger.email_tagger import EmailTaggerService
from application.servers.grpc.rta import rta
from application.servers.grpc.rta.rta import RtaService
from starlette.requests import Request
from starlette.responses import JSONResponse

log = logging.getLogger(__name__)


@dataclass
class ServiceNumberEmailReceived(Scenario):
    name: str = "Service number email received"

    async def run(self) -> ScenarioResult:
        # given ...
        # - The email is a repair email
        tag_id = 1
        email_tagger_prediction = email_tagger.prediction_response(predictions=[prediction(tag_id=tag_id)])
        self.given(EmailTaggerService.path("GetPrediction"), WillReturn(email_tagger_prediction))

        # - a service number was detected in emails body
        service_number = "any_service_number"
        rta_prediction = rta.prediction_response(potential_service_numbers=[service_number])
        self.given(RtaService.path("GetPrediction"), WillReturn(rta_prediction))

        # - The detected service number exists in Bruin
        inventory = Inventory(documents=[Document(serviceNumber=service_number)])
        self.given("/api/Inventory", WillReturnJSON(inventory))

        # - No active tickets were found for the service number
        no_tickets = TicketBasic()
        self.given("/api/Ticket/basic", WillReturnJSON(no_tickets))

        # - The detected service number can be included in a VOO ticket
        ticket_topics = TicketTopics(callTypes=[CallType(category="VOO")])
        self.given("/api/Ticket/topics", WillReturnJSON(ticket_topics))

        # - A ticket was created
        created_ticket = hash("any_created_ticket_id")
        ticket_repair = TicketRepair(items=[Item(ticketId=created_ticket)])
        self.given("/api/Ticket/repair", WillReturnJSON(ticket_repair))

        # when
        email = Email()
        email_id = email.Notification.Body.EmailId
        await bruin.notify_email(email)

        # then
        return await self.check(
            # [email-tagger] the email was tagged in Bruin
            self.route(f"/api/Email/{email_id}/tag/{tag_id}").was_reached(timeout.RTA),
            # [rta] a ticket was upserted
            self.route(f"/api/Ticket/repair").was_reached(timeout.RTA),
            # [rta] notes were appended for created ticket
            self.route(f"/api/Ticket/{created_ticket}/notes/advanced").was_reached(timeout.RTA),
            # [rta] created ticket was linked
            self.route(f"/api/Email/{email_id}/link/ticket/{created_ticket}").was_reached(timeout.RTA),
            # [rta] user was subscribed to the created ticket
            self.route(f"/api/Ticket/{created_ticket}/subscribeUser").was_reached(timeout.RTA),
            # [rta] konstellation was sent the result of RTA
            self.route(RtaService.path("SaveOutputs")).was_reached(timeout.RTA),
            # [rta] mail was marked as Done
            self.route(f"/api/Email/status").was_reached(timeout.RTA),
        )


@dataclass
class TicketNumberEmailReceived(Scenario):
    name: str = "Ticket number email received"

    async def run(self):
        # given ...
        # - The email is a repair email
        tag_id = 1
        email_tagger_prediction = email_tagger.prediction_response(predictions=[prediction(tag_id=tag_id)])
        self.given(EmailTaggerService.path("GetPrediction"), WillReturn(email_tagger_prediction))

        # - a ticket number was detected in emails body
        ticket_number = hash("any_ticket_number")
        rta_prediction = rta.prediction_response(potential_ticket_numbers=[str(ticket_number)])
        self.given(RtaService.path("GetPrediction"), WillReturn(rta_prediction))

        # - The detected ticket number exists in Bruin
        single_ticket = TicketBasic(total=1, responses=[Response(ticketID=ticket_number)])

        async def ticket_basic(request: Request):
            if request.query_params.get("TicketID") == str(ticket_number):
                return JSONResponse(single_ticket.dict())
            else:
                return JSONResponse(TicketBasic().dict())

        self.given("/api/Ticket/basic", WillExecute(ticket_basic))

        # when
        email = Email()
        email_id = email.Notification.Body.EmailId
        await bruin.notify_email(email)

        # then
        return await self.check(
            # [email-tagger] the email was tagged in Bruin
            self.route(f"/api/Email/{email_id}/tag/{tag_id}").was_reached(timeout.RTA),
            # [rta] notes were appended for detected ticket
            self.route(f"/api/Ticket/{ticket_number}/notes").was_reached(timeout.RTA),
            # [rta] detected ticket was linked
            self.route(f"/api/Email/{email_id}/link/ticket/{ticket_number}").was_reached(timeout.RTA),
            # [rta] konstellation was sent the result of RTA
            self.route(RtaService.path("SaveOutputs")).was_reached(timeout.RTA),
            # [rta] mail was marked as Done
            self.route(f"/api/Email/status").was_reached(timeout.RTA),
        )


@dataclass
class CreatedTicketsFeedback(Scenario):
    name: str = "Created tickets feedback"

    async def run(self):
        # given ...
        # - a ticket exists
        ticket_number = hash("any_ticket_number")
        single_ticket = TicketBasic(total=1, responses=[Response(ticketID=ticket_number)])

        async def ticket_basic(request: Request):
            if request.query_params.get("TicketID") == str(ticket_number):
                return JSONResponse(single_ticket.dict())
            else:
                return JSONResponse(TicketBasic().dict())

        self.given("/api/Ticket/basic", WillExecute(ticket_basic))

        # - Bruin will return the details of the ticket
        service_number = "any_service_number"
        ticket_details = TicketDetails(ticketNotes=[TicketNote(serviceNumber=[service_number])])
        self.given(f"/api/Ticket/{ticket_number}/details", WillReturnJSON(ticket_details))

        # - The service number exists in Bruin
        inventory = Inventory(documents=[Document(serviceNumber=service_number)])
        self.given("/api/Inventory", WillReturnJSON(inventory))

        # when
        email = Email()
        # Needed for KRE integration, else it crashes without any log. ('parent_id' being retrieved with [] notation)
        # Don't know why this is being sent to the tickets webhook.
        # Could it be that ParentId is the parent email that is linked to the ticket?
        email.Notification.Body.ParentId = hash("any_parent_id")
        email.Notification.Body.Ticket = TicketModel(TicketId=str(ticket_number))
        await bruin.notify_ticket(email)

        # then
        return await self.check(
            # [rta] metrics were saved in Konstellation
            self.route(EmailTaggerService.path("SaveMetrics")).was_reached(timeout.EMAIL_TAGGER),
            # [rta] feedback was saved in Konstellation
            self.route(RtaService.path("SaveCreatedTicketsFeedback")).was_reached(timeout.RTA),
        )


@dataclass
class AutoReply(Scenario):
    name: str = "Auto reply"

    async def run(self) -> ScenarioResult:
        # given ...
        # - The parent email is a repair email
        tag_id = 1
        email_tagger_prediction = email_tagger.prediction_response(predictions=[prediction(tag_id=tag_id)])
        self.given(EmailTaggerService.path("GetPrediction"), WillReturn(email_tagger_prediction))

        # - no service numbers were detected in parent emails body
        rta_prediction = rta.prediction_response(potential_service_numbers=[])
        self.given(RtaService.path("GetPrediction"), WillReturn(rta_prediction))

        # - parent email is received
        parent_email = Email()
        parent_email_id = parent_email.Notification.Body.EmailId
        await bruin.notify_email(parent_email)

        result = await self.check(
            self.route(RtaService.path("SaveOutputs")).was_reached(timeout.RTA),
            self.route("/api/Email/status").was_reached(timeout.RTA),
            self.route(f"/api/Notification/email/ReplyAll").was_reached(timeout.RTA),
        )

        if not result.passed:
            return result

        # - a service number was detected in emails body
        service_number = "any_service_number"
        rta_prediction = rta.prediction_response(potential_service_numbers=[service_number])
        self.given(RtaService.path("GetPrediction"), WillReturn(rta_prediction))

        # - The detected service number exists in Bruin
        inventory = Inventory(documents=[Document(serviceNumber=service_number)])
        self.given("/api/Inventory", WillReturnJSON(inventory))

        # - No active tickets were found for the service number
        no_tickets = TicketBasic()
        self.given("/api/Ticket/basic", WillReturnJSON(no_tickets))

        # - The detected service number can be included in a VOO ticket
        ticket_topics = TicketTopics(callTypes=[CallType(category="VOO")])
        self.given("/api/Ticket/topics", WillReturnJSON(ticket_topics))

        # - A ticket was created
        created_ticket = hash("any_created_ticket_id")
        ticket_repair = TicketRepair(items=[Item(ticketId=created_ticket)])
        self.given("/api/Ticket/repair", WillReturnJSON(ticket_repair))

        # when...
        answer_email = Email()
        answer_email.Notification.Body.ParentId = parent_email_id
        answer_email_id = answer_email.Notification.Body.EmailId
        await bruin.notify_email(answer_email)

        # then
        return await self.check(
            # [rta] a ticket was upserted
            self.route(f"/api/Ticket/repair").was_reached(timeout.RTA),
            # [rta] notes were appended for created ticket
            self.route(f"/api/Ticket/{created_ticket}/notes/advanced").was_reached(timeout.RTA),
            # [rta] created ticket was linked
            self.route(f"/api/Email/{answer_email_id}/link/ticket/{created_ticket}").was_reached(timeout.RTA),
            self.route(f"/api/Email/{parent_email_id}/link/ticket/{created_ticket}").was_reached(timeout.RTA),
            # [rta] user was subscribed to the created ticket
            self.route(f"/api/Ticket/{created_ticket}/subscribeUser").was_reached(timeout.RTA),
            # [rta] konstellation was sent the result of RTA
            self.route(RtaService.path("SaveOutputs")).was_reached(timeout.RTA),
            # [rta] mail was marked as Done
            self.route(f"/api/Email/status").was_reached(timeout.RTA),
        )


bruin_webhook_scenarios = [
    ServiceNumberEmailReceived(),
    TicketNumberEmailReceived(),
    CreatedTicketsFeedback(),
    AutoReply(),
]
