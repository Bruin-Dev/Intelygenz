## Execute action to consume message

* If service's action is not properly set up:
  ```python
  self.logger.error(f'The object {self.state_instance} has no method named {self.target_function}')
  ```
  END

[__check_large_messages_decorator](../eventbus/__check_large_messages_decorator.md) is implicitly called before
executing the action for the message
