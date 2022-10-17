import logging
from dataclasses import dataclass, field

from application.domain.device import Device, DeviceId
from application.domain.errors import AutoResolutionError
from application.domain.note import Note
from application.domain.ticket import TicketStatus
from application.repositories import BruinRepository, ForticloudRepository, build_note
from application.repositories.metrics_repository import MetricsRepository

log = logging.getLogger(__name__)


@dataclass
class CheckDevice:
    forticloud_repository: ForticloudRepository = field(repr=False)
    bruin_repository: BruinRepository = field(repr=False)
    metrics_repository: MetricsRepository = field(repr=False)

    async def __call__(self, device_id: DeviceId):
        log.debug(f"check_device(device_id={device_id}")

        device = await self.forticloud_repository.get_device(device_id)
        if device.is_offline:
            log.debug(f"Handling offline device {device.id}")
            await self._handle_offline_device(device)
        else:
            log.debug(f"Handling online device {device.id}")
            await self._handle_online_device(device)

    async def _handle_online_device(self, online_device: Device):
        log.debug(f"Device {online_device.id} is online. Trying to auto-resolve corresponding task.")

        # Find a corresponding open ticket for the online device
        current_ticket = await self.bruin_repository.find_open_automation_ticket_for(device_id=online_device.id)
        if not current_ticket:
            log.debug(f"Device {online_device.id} has no open ticket at the moment.")
            return

        # Try to auto resolve the ticket
        try:
            auto_resolved_task = current_ticket.auto_resolve(online_device.id.service_number)
        except AutoResolutionError as e:
            log.debug(f"Device {online_device.id} couldn't be auto-resolved: {e}")
            return

        # Once the business validation passed, try to un-pause the auto-resolved task.
        try:
            await self.bruin_repository.unpause_task(ticket_id=current_ticket.id, task=auto_resolved_task)
        except Exception as e:
            log.warning(f"Error un-pausing Bruin task {current_ticket.id} in ticket {current_ticket.id}: {e}")

        # Try to resolve the auto-resolved task in Bruin.
        try:
            await self.bruin_repository.resolve_task(ticket_id=current_ticket.id, task=auto_resolved_task)
            await self.metrics_repository.add_auto_resolved_task_metric()
        except Exception as e:
            log.warning(f"Error resolving Bruin task {auto_resolved_task.id}: {e}")
            return

        # Once the task was resolved in Bruin, try to add an auto-resolve note.
        try:
            await self.bruin_repository.post_ticket_note(
                note=Note(
                    ticket_id="any_ticket_id",
                    service_number=auto_resolved_task.service_number,
                    text=auto_resolved_task.auto_resolution_note_text,
                )
            )
        except Exception as e:
            log.warning(f"Error posting Bruin note to {current_ticket.id}: {e}")

        log.debug(f"Task {auto_resolved_task.id} in ticket {current_ticket.id} was auto-resolved")

    async def _handle_offline_device(self, offline_device: Device):
        log.debug(f"Device {offline_device.id} is offline. Creating ticket.")
        created_ticket = await self.bruin_repository.post_repair_ticket(offline_device.id)

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
                        service_number=offline_device.id.service_number,
                        text=build_note(offline_device),
                    )
                )
            case TicketStatus.IN_PROGRESS:
                log.debug(
                    f"Trouble affecting {offline_device} is currently being addressed "
                    f"in ticket {created_ticket.ticket_id}"
                )
            case TicketStatus.FAILED_REOPENING:
                raise Exception(f"The existing {created_ticket.ticket_id} could not be reopened")
            case TicketStatus.REOPENED:
                log.debug(
                    f"Posting a Re-opening note for the affected device {offline_device} "
                    f"in ticket {created_ticket.ticket_id}"
                )
                await self.bruin_repository.post_ticket_note(
                    Note(
                        ticket_id=created_ticket.ticket_id,
                        service_number=offline_device.id.service_number,
                        text=build_note(offline_device, is_reopen_note=True),
                    )
                )
            case TicketStatus.REOPENED_SAME_LOCATION:
                log.debug(
                    f"Posting a new triage note for the affected device {offline_device} "
                    f"in ticket {created_ticket.ticket_id}"
                )
                await self.bruin_repository.post_ticket_note(
                    Note(
                        ticket_id=created_ticket.ticket_id,
                        service_number=offline_device.id.service_number,
                        text=build_note(offline_device),
                    )
                )
