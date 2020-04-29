from shortuuid import uuid
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil import tz


class TicketRepository:

    def __init__(self, config, logger, event_bus):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus

    async def ticket_is_resolved(self, ticket_id):
        get_ticket_payload = {'request_id': uuid(), 'client_id': None,
                              'ticket_status': ['New', 'InProgress', 'Draft'],
                              'category': 'SD-WAN',
                              'ticket_id': ticket_id,
                              'ticket_topic': ""
                              }
        ticket_response = await self._event_bus.rpc_request("bruin.ticket.request",
                                                            get_ticket_payload,
                                                            timeout=90)

        if len(ticket_response["tickets"]) > 0:
            return False
        return True

    async def change_detail_work_queue(self, ticket_id, detail_id, serial_number, queue_name):
        change_work_queue_payload = {
            "request_id": uuid(),
            "filters": {
                "service_number": serial_number,
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "queue_name": queue_name,
            }
        }
        result = await self._event_bus.rpc_request("bruin.ticket.change.work", change_work_queue_payload, timeout=60)
        return result

    async def _ticket_is_old_enough(self, ticket_id):
        get_ticket_payload = {'request_id': uuid(), 'client_id': None,
                              'ticket_status': ['New', 'InProgress', 'Draft'],
                              'category': 'SD-WAN',
                              'ticket_id': ticket_id,
                              'ticket_topic': ""
                              }
        ticket_response = await self._event_bus.rpc_request("bruin.ticket.request",
                                                            get_ticket_payload,
                                                            timeout=90)
        tickets = ticket_response.get('tickets')

        if tickets:
            ticket = tickets[0]
            # Bruin returns here creation date as timezone-naive but is UTC
            creation_date = parse(ticket["createDate"] + " UTC")
            now = datetime.now(tz=tz.UTC)
            ticket_age_in_minutes = (now - creation_date).total_seconds() / 60
            if ticket_age_in_minutes > self._config.CONDITIONS["ticket_min_age_minutes"]:
                return True
        return False

    async def get_ticket_current_task(self, ticket_id, serial_number):
        get_ticket_task_payload = {'request_id': uuid(),
                                   "filters": {'ticket_id': ticket_id},
                                   }

        ticket_task_history_response = await self._event_bus.rpc_request("bruin.ticket.get.task.history",
                                                                         get_ticket_task_payload,
                                                                         timeout=90)

        # The current Task Result will be the one in the last registry that doesn't have any null
        task_registries = ticket_task_history_response.get('body')

        task_registries.sort(key=lambda r: r["EnteredDate_N"])
        # Remove any registry that doesn't belong to the asset (serial) we're working with
        task_registries = [registry for registry in task_registries if
                           registry.get('Asset') and serial_number in registry.get('Asset')]

        # A literal is needed for the map of "Current status --> [automatable statuses]".None is T7's null task result
        current_task_result = "None"

        # Use serial here to only read registries for that asset
        for task_registry in task_registries:
            current_task_candidate = task_registry.get("Task Result")
            if current_task_candidate:
                current_task_result = current_task_candidate

        return current_task_result
