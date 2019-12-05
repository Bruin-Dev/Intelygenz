import json


class DevelopmentAction:
    def __init__(self, logger, event_bus, template_renderer, config):
        self._logger = logger
        self._event_bus = event_bus
        self._template_renderer = template_renderer
        self._config = config

    async def run_action(self, device, edge_status, trouble, ticket_dict):
        self._logger.info(f'Service affecting trouble {trouble} detected in edge with data {edge_status}')
