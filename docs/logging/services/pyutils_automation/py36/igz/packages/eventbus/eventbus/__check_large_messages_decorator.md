## Recover message before consuming it

* If message is stored to an external storage:
  [recover_message](../storage_managers/recover_message.md)

  ```python
  self._logger.info(
      f'Message received from topic {event} indicates that the actual message was larger than 1MB '
      f'and was stored with {type(self._messages_storage_manager).__name__}.'
  )
  ```

[_cb_with_action](../../nats/clients/_cb_with_action.md) is implicitly called