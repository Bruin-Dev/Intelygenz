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
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(module)s: %(levelname)s: %(message)s',
                                handlers=[logging.StreamHandler(sys.stdout)])
            logger = logging.getLogger('action-wrapper')
        self.logger = logger

    def execute_stateful_action(self, data):
        if getattr(self.state_instance, self.target_function) is None:
            self.logger.error(f'The object {self.state_instance} has no method named {self.target_function}')
            return
        return getattr(self.state_instance, self.target_function)(data)
