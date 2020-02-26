from shortuuid import uuid
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil import tz


class TicketRepository:

    def __init__(self, config, logger, event_bus):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus

    async def get_all_valid_tickets_with_serial_and_detail(self):
        all_tickets = []
        for company in self._config.CUSTOMER_LIST:
            all_company_tickets = await self._get_all_tickets_by_client_id(list(company.keys())[0])
            old_enough_tickets = [ticket for ticket in all_company_tickets
                                  if await self._ticket_is_old_enough(ticket)]
            for ticket in old_enough_tickets:
                detail = await self._get_detail_id_and_serial_by_serial_list(ticket, list(company.values())[0])
                if detail:
                    ticket_object = self._build_ticket_object(ticket, detail)
                    all_tickets.append(ticket_object)
        return all_tickets

    @staticmethod
    def _build_ticket_object(ticket_id, detail):
        return {"ticket_id": ticket_id, "serial_number": detail["serial_number"], "detail_id": detail["detail_id"]}

    async def _get_all_tickets_by_client_id(self, bruin_client_id):
        request_outage_tickets_message = {'request_id': uuid(), 'client_id': bruin_client_id,
                                          'ticket_status': ['New', 'InProgress', 'Draft'],
                                          'category': 'SD-WAN',
                                          'ticket_topic': 'VOO'}
        outage_ticket_response = await self._event_bus.rpc_request("bruin.ticket.request",
                                                                   request_outage_tickets_message,
                                                                   timeout=90)

        parsed_outage_tickets = [ticket["ticketID"] for ticket in outage_ticket_response["tickets"]]

        request_affecting_tickets_message = {'request_id': uuid(), 'client_id': bruin_client_id,
                                             'ticket_status': ['New', 'InProgress', 'Draft'],
                                             'category': 'SD-WAN',
                                             'ticket_topic': 'VAS'}
        affecting_tickets_response = await self._event_bus.rpc_request("bruin.ticket.request",
                                                                       request_affecting_tickets_message,
                                                                       timeout=90)
        parsed_affecting_tickets = [ticket["ticketID"] for ticket in affecting_tickets_response["tickets"]]

        all_tickets = parsed_outage_tickets + parsed_affecting_tickets

        return all_tickets

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

    async def _get_detail_id_and_serial_by_serial_list(self, ticket_id, serials_list):
        detail = None
        ticket_detail_msg = {'request_id': uuid(),
                             'ticket_id': ticket_id}
        ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                           ticket_detail_msg,
                                                           timeout=15)

        for ticket_detail in ticket_details['ticket_details']['ticketDetails']:
            detail_value = ticket_detail.get('detailValue')
            if detail_value and detail_value in serials_list:
                detail = {
                    "detail_id": ticket_detail.get('detailID'),
                    "serial_number": detail_value
                }
                break

        return detail

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

    async def get_ticket_current_task(self, ticket_id):
        get_ticket_task_payload = {'request_id': uuid(),
                                   "filters": {'ticket_id': ticket_id},
                                   }

        ticket_task_history_response = await self._event_bus.rpc_request("bruin.ticket.get.task.history",
                                                                         get_ticket_task_payload,
                                                                         timeout=90)

        # The current Task Result will be the one in the last registry that doesn't have any null
        task_registries = ticket_task_history_response.get('body')

        task_registries.sort(key=lambda r: r["EnteredDate_N"])

        # A literal is needed for the map of "Current status --> [automatable statuses]".None is T7's null task result
        current_task_result = "None"

        for task_registry in task_registries:
            current_task_candidate = task_registry.get("Task Result")
            if current_task_candidate:
                current_task_result = current_task_candidate

        return current_task_result
