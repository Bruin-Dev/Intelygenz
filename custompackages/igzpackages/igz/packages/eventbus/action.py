class ActionWrapper:
    state_instance = None
    target_function = None
    is_async = False

    def __init__(self, state_instance: object, target_function: str, is_async=False):
        self.state_instance = state_instance
        self.target_function = target_function
        self.is_async = is_async

    def execute_stateful_action(self, data):
        if getattr(self.state_instance, self.target_function) is None:
            print(f'The object {self.state_instance} has no method named {self.target_function}')
            return
        return getattr(self.state_instance, self.target_function)(data)
