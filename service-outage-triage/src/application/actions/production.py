import json
import re
from shortuuid import uuid


class ProductionAction:

    def __init__(self, logger, event_bus, template_renderer, config):
        self._logger = logger
        self._event_bus = event_bus
        self._template_renderer = template_renderer
        self._config = config

    async def run_triage_action(self, ticket_dict, ticket_id):
        ticket_note = self._ticket_object_to_string(ticket_dict)
        await self._make_rpc_requests("Triage", ticket_id, ticket_note)

    async def run_event_action(self, event_note, ticket_id):
        await self._make_rpc_requests("Events", ticket_id, event_note)

    async def _make_rpc_requests(self, note_type, ticket_id, ticket_note):
        ticket_append_note_msg = {'request_id': uuid(),
                                  'ticket_id': ticket_id,
                                  'note': ticket_note}
        await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                          json.dumps(ticket_append_note_msg),
                                          timeout=15)
        slack_message = {'request_id': uuid(),
                         'message': f'{note_type} appended to ticket: '
                                    f'https://app.bruin.com/helpdesk?clientId=85940&'
                                    f'ticketId={ticket_id}, in '
                                    f'{self._config.ENV_CONFIG["environment"]}'}
        await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message),
                                          timeout=10)

    def _ticket_object_to_string(self, ticket_dict):
        edge_triage_str = "#*Automation Engine*# \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str
