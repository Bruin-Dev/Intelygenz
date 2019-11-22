import json


class DevelopmentAction:
    def __init__(self, logger, event_bus, template_renderer, config):
        self._logger = logger
        self._event_bus = event_bus
        self._template_renderer = template_renderer
        self._config = config

    async def run_action(self, device, edge_status, trouble, ticket_dict):
        email_obj = self._template_renderer._compose_email_object(edge_status, trouble, ticket_dict)
        await self._event_bus.rpc_request("notification.email.request", json.dumps(email_obj), timeout=10)
