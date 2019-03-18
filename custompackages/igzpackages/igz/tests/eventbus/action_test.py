from igz.packages.eventbus.action import ActionWrapper
from unittest.mock import Mock
import logging


class TestActionWrapper:

    def instantiation_test(self):
        state_instance = Mock()
        state_instance.target_function = Mock()
        mock_logger = Mock()
        action_wrapper = ActionWrapper(state_instance, state_instance.target_function)
        action_wrapper_2 = ActionWrapper(state_instance, state_instance.target_function, logger=mock_logger)
        assert action_wrapper.state_instance is state_instance
        assert action_wrapper.target_function is state_instance.target_function
        assert isinstance(action_wrapper.logger, logging._loggerClass) is True
        assert action_wrapper.logger.hasHandlers() is True
        assert action_wrapper.logger.getEffectiveLevel() is 10
        assert action_wrapper_2.logger is mock_logger

    def execute_action_with_action_test(self):
        mock_logger = Mock()
        state_instance = Mock()
        state_instance.target_function = Mock(return_value="OK")
        action_wrapper = ActionWrapper(state_instance, "target_function", logger=mock_logger)
        assert action_wrapper.execute_stateful_action("SomeData") is "OK"

    def execute_action_KO_no_function_test(self):
        mock_logger = Mock()
        state_instance = Mock()
        state_instance.othermethod = None
        action_wrapper = ActionWrapper(state_instance, "othermethod", logger=mock_logger)
        assert action_wrapper.execute_stateful_action("SomeData") is not "OK"
