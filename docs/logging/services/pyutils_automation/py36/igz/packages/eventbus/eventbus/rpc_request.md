## Publish request message to the bus

* If request message is too large for NATS to handle (1MB+):

  [store_message](../storage_managers/store_message.md)

  ```python
  self._logger.info(
      'Message received in rpc_request() was larger than 1MB so it was stored with '
      f'{type(self._messages_storage_manager).__name__}. The token needed to recover it is '
      f'{message["token"]}.'
  )
  ```

```python
self._logger.info(f"Requesting a response from subject {subject}...")
```

[rpc_request](../../nats/clients/rpc_request.md)

```python
self._logger.info(f"Response received from a replier subscribed to subject {topic}")
```

* If response message is stored to an external storage:
  ```python
  self._logger.info(
      f'Message received from topic {topic} indicates that the actual message was larger than 1MB '
      f'and was stored with {type(self._messages_storage_manager).__name__}.'
  )
  ```
  [recover_message](../storage_managers/recover_message.md)
