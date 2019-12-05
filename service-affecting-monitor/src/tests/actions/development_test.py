from unittest.mock import Mock

import pytest
from application.actions.development import DevelopmentAction
from asynctest import CoroutineMock


class TestDevelopmentAction:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        template_renderer = Mock()
        config = Mock()

        development_action = DevelopmentAction(logger, event_bus, template_renderer, config)

        assert development_action._logger == logger
        assert development_action._event_bus == event_bus
        assert development_action._config == config

    @pytest.mark.asyncio
    async def run_action_test(self):
        logger = Mock()
        logger.info = Mock()
        config = Mock()

        template_renderer = Mock()

        event_bus = Mock()

        device = Mock()
        edge_status = 'Some Edge Status'
        trouble = 'LATENCY'
        ticket_dict = {'test': 'dict'}

        development_action = DevelopmentAction(logger, event_bus, template_renderer, config)

        await development_action.run_action(device, edge_status, trouble, ticket_dict)

        logger.info.assert_called_once()
