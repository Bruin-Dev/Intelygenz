import json
import re
from shortuuid import uuid


class ProductionAction:

    def __init__(self, logger, event_bus, template_renderer, config):
        self._logger = logger
        self._event_bus = event_bus
        self._template_renderer = template_renderer
        self._config = config

    async def run_action(self, device, edge_status, trouble, ticket_dict):
        client_id = edge_status['edge_info']['enterprise_name'].split('|')[1]
        ticket_exists = await self._ticket_existence(client_id, edge_status['edge_info']['edges']['serialNumber'],
                                                     trouble)
        if ticket_exists is False:
            # TODO contact is hardcoded. When Mettel provides us with a service to retrieve the contact
            # TODO for each site, we should change this hardcode
            ticket_note = self._ticket_object_to_string(ticket_dict)
            ticket_details = {
                "request_id": uuid(),
                "clientId": client_id,
                "category": "VAS",
                "services": [
                    {
                        "serviceNumber": device['serial']
                    }
                ],
                "contacts": [
                    {
                        "email": device['email'],
                        "phone": device['phone'],
                        "name": device['name'],
                        "type": "site"
                    },
                    {
                        "email": device['email'],
                        "phone": device['phone'],
                        "name": device['name'],
                        "type": "ticket"
                    }
                ]
            }
            ticket_id = await self._event_bus.rpc_request("bruin.ticket.creation.request",
                                                          json.dumps(ticket_details), timeout=30)
            ticket_append_note_msg = {'request_id': uuid(),
                                      'ticket_id': ticket_id["ticketIds"]["ticketIds"][0],
                                      'note': ticket_note}
            await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                              json.dumps(ticket_append_note_msg),
                                              timeout=15)

            slack_message = {'request_id': uuid(),
                             'message': f'Ticket created with ticket id: {ticket_id["ticketIds"]["ticketIds"][0]}\n'
                                        f'https://app.bruin.com/helpdesk?clientId=85940&'
                                        f'ticketId={ticket_id["ticketIds"]["ticketIds"][0]} , in '
                                        f'{self._config.ENV_CONFIG["environment"]}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message),
                                              timeout=10)

            self._logger.info(f'Ticket created with ticket id: {ticket_id["ticketIds"]["ticketIds"][0]}')

    async def _ticket_existence(self, client_id, serial, trouble):
        ticket_request_msg = {'request_id': uuid(), 'client_id': client_id,
                              'ticket_status': ['New', 'InProgress', 'Draft'],
                              'category': 'SD-WAN', 'ticket_topic': 'VAS'}
        all_tickets = await  self._event_bus.rpc_request("bruin.ticket.request",
                                                         json.dumps(ticket_request_msg, default=str),
                                                         timeout=15)
        for ticket in all_tickets['tickets']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'ticket_id': ticket['ticketID']}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                               json.dumps(ticket_detail_msg, default=str),
                                                               timeout=15)
            for ticket_detail in ticket_details['ticket_details']['ticketDetails']:
                if 'detailValue' in ticket_detail.keys():
                    if ticket_detail['detailValue'] == serial:
                        for ticket_note in (ticket_details['ticket_details']['ticketNotes']):
                            if ticket_note['noteValue'] is not None:
                                if trouble in ticket_note['noteValue']:
                                    return True
        return False

    def _ticket_object_to_string(self, ticket_dict):
        edge_triage_str = "#*Automation Engine*# \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str
