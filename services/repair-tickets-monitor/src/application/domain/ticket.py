from enum import Enum

from dataclasses import dataclass


@dataclass
class Ticket:
    id: str
    site_id: str = None
    status: 'TicketStatus' = None
    call_type: str = None
    category: str = None

    # We will keep this here for now but it may need to be refactored somewhere else
    # as active tickets status should not be hardcoded
    def is_active(self):
        return self.status in [status.value for status in ACTIVE_TICKET_STATUS]

    # We will keep this here for now but it may need to be refactored somewhere else
    # as repair categories should not be hardcoded
    def is_repair(self):
        return self.category in [category.value for category in REPAIR_CATEGORIES]


class Category(str, Enum):
    SERVICE_AFFECTING = "VAS"
    SERVICE_OUTAGE = "VOO"
    WIRELESS_SERVICE_NOT_WORKING = "019"


class TicketStatus(str, Enum):
    CLOSED = "Closed"
    NEW = "New"
    RESOLVED = "Resolved"
    DRAFT = "Draft"
    IN_PROGRESS = "InProgress"
    IN_REVIEW = "InReview"
    UNKNOWN = None


# These constants should not be hardcoded.
# To be refactored into a new entity or aggregate root with a get_operable_tickets method
REPAIR_CATEGORIES = [Category.SERVICE_OUTAGE, Category.SERVICE_AFFECTING]
ACTIVE_TICKET_STATUS = [TicketStatus.NEW, TicketStatus.IN_PROGRESS]
