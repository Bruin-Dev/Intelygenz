from igz.packages.eventbus.action import ActionWrapper
from unittest.mock import Mock
from igz.packages.Logger.logger_client import LoggerClient
from igz.config import testconfig as config


class TestActionWrapper:

    logger = LoggerClient(config).get_logger()

    def instantiation_test(self):
        state_instance = Mock()
        state_instance.target_function = Mock()
        action_wrapper = ActionWrapper(self.logger, state_instance, state_instance.target_function)
        assert action_wrapper.state_instance is state_instance
        assert action_wrapper.target_function is state_instance.target_function

    def execute_action_with_action_test(self):
        state_instance = Mock()
        state_instance.target_function = Mock(return_value="OK")
        action_wrapper = ActionWrapper(self.logger, state_instance, "target_function")
        assert action_wrapper.execute_stateful_action("SomeData") is "OK"

    def execute_action_KO_no_function_test(self):
        state_instance = Mock()
        state_instance.othermethod = None
        action_wrapper = ActionWrapper(self.logger, state_instance, "othermethod")
        assert action_wrapper.execute_stateful_action("SomeData") is not "OK"
