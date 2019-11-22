import json

from shortuuid import uuid


class DevelopmentAction:

    def __init__(self, logger, event_bus, template_renderer, config):
        self._logger = logger
        self._event_bus = event_bus
        self._template_renderer = template_renderer
        self._config = config

    async def run_triage_action(self, ticket_dict, ticket_id):
        ticket_note = self._template_renderer._ticket_object_to_email_obj(ticket_dict)
        await self._event_bus.rpc_request("notification.email.request",
                                          json.dumps(ticket_note),
                                          timeout=10)
        slack_message = {'request_id': uuid(),
                         'message': f'Triage appended to ticket: '
                                    f'https://app.bruin.com/helpdesk?clientId=85940&ticketId='
                                    f'{ticket_id}, in '
                                    f'{self._config.ENV_CONFIG["environment"]}'}
        await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)

    async def run_event_action(self, event_note, ticket_id):
        pass
