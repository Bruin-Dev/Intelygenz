from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetTickets(Subscription):
    subject: str = "bruin.ticket.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetTicketsBasic(Subscription):
    subject: str = "bruin.ticket.basic.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetSingleTicketBasic(Subscription):
    subject: str = "bruin.single_ticket.basic.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetTicketDetails(Subscription):
    subject: str = "bruin.ticket.details.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetTicketOverview(Subscription):
    subject: str = "bruin.ticket.overview.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class PostNoteToTicket(Subscription):
    subject: str = "bruin.ticket.note.append.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class PostMultipleNotesToTicket(Subscription):
    subject: str = "bruin.ticket.multiple.notes.append.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class CreateTicket(Subscription):
    subject: str = "bruin.ticket.creation.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class OpenTicketTask(Subscription):
    subject: str = "bruin.ticket.status.open"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class ResolveTicketTask(Subscription):
    subject: str = "bruin.ticket.status.resolve"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetSerialNumberFromInventoryAttributes(Subscription):
    subject: str = "bruin.inventory.attributes.serial"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetManagementStatus(Subscription):
    subject: str = "bruin.inventory.management.status"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class CreateOutageTicket(Subscription):
    subject: str = "bruin.ticket.creation.outage.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetCustomerInfoByServiceNumber(Subscription):
    subject: str = "bruin.customer.get.info"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetCustomerInfoByDID(Subscription):
    subject: str = "bruin.customer.get.info_by_did"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class ChangeWorkQueueForTicketTask(Subscription):
    subject: str = "bruin.ticket.change.work"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetTicketTaskHistory(Subscription):
    subject: str = "bruin.ticket.get.task.history"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetAvailableWorkQueuesForTask(Subscription):
    subject: str = "bruin.ticket.detail.get.next.results"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class UnpauseTicketTask(Subscription):
    subject: str = "bruin.ticket.unpause"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class TagEmail(Subscription):
    subject: str = "bruin.email.tag.request"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetServiceNumberByCircuitId(Subscription):
    subject: str = "bruin.get.circuit.id"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class ChangeTicketSeverity(Subscription):
    subject: str = "bruin.change.ticket.severity"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetSiteInfo(Subscription):
    subject: str = "bruin.get.site"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class MarkBruinEmailAsDone(Subscription):
    subject: str = "bruin.mark.email.done"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class LinkBruinEmailToTicket(Subscription):
    subject: str = "bruin.link.ticket.email"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class SendEmailMilestoneNotification(Subscription):
    subject: str = "bruin.notification.email.milestone"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class GetAvailableTopicsForAsset(Subscription):
    subject: str = "bruin.get.asset.topics"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class SubscribeUserToTicket(Subscription):
    subject: str = "bruin.subscribe.user"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class UpdateBruinEmailStatus(Subscription):
    subject: str = "bruin.email.status"
    queue: str = "bruin_bridge"


@dataclass(kw_only=True)
class ReplyToAllContactsInBruinEmail(Subscription):
    subject: str = "bruin.email.reply"
    queue: str = "bruin_bridge"
