import logging
from dataclasses import dataclass, field

from application.models.device import DeviceId
from application.models.note import Note
from application.models.ticket import TicketStatus
from application.repositories import BruinRepository, ForticloudRepository, build_note

log = logging.getLogger(__name__)


@dataclass
class CheckDevice:
    forticloud_repository: ForticloudRepository = field(repr=False)
    bruin_repository: BruinRepository = field(repr=False)

    async def __call__(self, device_id: DeviceId):
        log.debug(f"check_device(device_id={device_id}")

        device = await self.forticloud_repository.get_device(device_id)
        if not device.is_offline:
            log.debug(f"Device {device.id} is online. Nothing to do.")
            return

        affected_device = device
        log.debug(f"Device {device.id} is offline. Creating ticket.")
        created_ticket = await self.bruin_repository.post_repair_ticket(device_id)

        # When the logic behind any match case will start to grow, it should be best to refactor it into domain events
        # Something in the lines of:
        # domain_events = ticket.add_trouble(affected_device)
        # for event in domain_events:
        #   match event.type:
        #      case AddTriageNote:
        #      case AddReopenNote:
        #      case ForwardHnoc:
        #      case SetTicketSeverity:
        match created_ticket.ticket_status:
            case TicketStatus.CREATED:
                log.debug(f"New ticket {created_ticket.ticket_id} created. Posting corresponding note.")
                await self.bruin_repository.post_ticket_note(
                    Note(
                        ticket_id=created_ticket.ticket_id,
                        service_number=affected_device.id.service_number,
                        text=build_note(device),
                    )
                )
            case TicketStatus.IN_PROGRESS:
                log.debug(
                    f"Trouble affecting {affected_device} is currently being addressed "
                    f"in ticket {created_ticket.ticket_id}"
                )
            case TicketStatus.FAILED_REOPENING:
                raise Exception(f"The existing {created_ticket.ticket_id} could not be reopened")
            case TicketStatus.REOPENED:
                log.debug(
                    f"Posting a Re-opening note for the affected device {affected_device} "
                    f"in ticket {created_ticket.ticket_id}"
                )
                await self.bruin_repository.post_ticket_note(
                    Note(
                        ticket_id=created_ticket.ticket_id,
                        service_number=affected_device.id.service_number,
                        text=build_note(device, is_reopen_note=True),
                    )
                )
            case TicketStatus.REOPENED_SAME_LOCATION:
                log.debug(
                    f"Posting a new triage note for the affected device {affected_device} "
                    f"in ticket {created_ticket.ticket_id}"
                )
                await self.bruin_repository.post_ticket_note(
                    Note(
                        ticket_id=created_ticket.ticket_id,
                        service_number=affected_device.id.service_number,
                        text=build_note(device),
                    )
                )
