import json
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch
from collections import OrderedDict

import pytest
from application.actions.notifier import NotifierAction
from application.actions.development import DevelopmentAction
from application.actions.production import ProductionAction

from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import development as development_module
from config import testconfig


class TestNotifierAction:

    def new_instance_dev_test(self):
        event_bus = Mock()
        config = testconfig

        notifier_action = NotifierAction(event_bus, config)

        assert isinstance(notifier_action, DevelopmentAction)

    def new_instance_pro_test(self):
        event_bus = Mock()
        config = testconfig

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = "production"

        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            notifier_action = NotifierAction(event_bus, config)

        assert isinstance(notifier_action, ProductionAction)

    def new_instance_none_test(self):
        event_bus = Mock()
        config = testconfig

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = "meaningless"

        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            notifier_action = NotifierAction(event_bus, config)

        assert isinstance(notifier_action, ProductionAction) is False
        assert isinstance(notifier_action, DevelopmentAction) is False
