import logging
import sys


class ActionWrapper:
    state_instance = None
    target_function = None
    is_async = False
    logger = None

    def __init__(self, state_instance: object, target_function: str, is_async=False, logger=None):
        self.state_instance = state_instance
        self.target_function = target_function
        self.is_async = is_async
        if logger is None:
            logger = logging.getLogger('action-wrapper')
            logger.setLevel(logging.DEBUG)
            log_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s: %(module)s: %(levelname)s: %(message)s')
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        self.logger = logger

    def execute_stateful_action(self, data):
        if hasattr(self.state_instance, self.target_function) is False:
            self.logger.error(f'The object {self.state_instance} has no method named {self.target_function}')
            return
        return getattr(self.state_instance, self.target_function)(data)
