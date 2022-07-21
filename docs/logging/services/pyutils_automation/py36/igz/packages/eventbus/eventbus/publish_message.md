## Publish message to the bus

```python
self._logger.info(f"Publishing message to subject {topic}...")
```

* If message is too large for NATS to handle (1MB+):

  [store_message](../storage_managers/store_message.md)

  ```python
  self._logger.info(
      'Message received in publish() was larger than 1MB so it was stored with '
      f'{type(self._messages_storage_manager).__name__}. The token needed to recover it is '
      f'{msg["token"]}.'
  )
  ```

[publish](../../nats/clients/publish.md)