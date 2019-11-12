from unittest.mock import Mock
from unittest.mock import patch

from igz.packages.notifier_action.notifier_action import NotifierAction

from igz.config import testconfig


class TestNotifierAction:

    def new_instance_dev_test(self):
        logger = Mock()
        event_bus = Mock()
        config = testconfig
        production_action = Mock()
        development_action = Mock()

        notifier_action = NotifierAction(logger, event_bus, config, production_action, development_action)

        assert notifier_action == development_action()

    def new_instance_pro_test(self):
        logger = Mock()
        event_bus = Mock()
        config = testconfig
        production_action = Mock()
        development_action = Mock()

        custom_triage_config = config.ENV_CONFIG.copy()
        custom_triage_config['environment'] = "production"

        with patch.dict(config.ENV_CONFIG, custom_triage_config):
            notifier_action = NotifierAction(logger, event_bus, config, production_action, development_action)

        assert notifier_action == production_action()

    def new_instance_none_test(self):
        logger = Mock()
        event_bus = Mock()
        config = testconfig
        production_action = Mock()
        development_action = Mock()

        custom_triage_config = config.ENV_CONFIG.copy()
        custom_triage_config['environment'] = "meaningless"

        with patch.dict(config.ENV_CONFIG, custom_triage_config):
            notifier_action = NotifierAction(logger, event_bus, config, production_action, development_action)

        assert notifier_action != development_action()
        assert notifier_action != production_action()
