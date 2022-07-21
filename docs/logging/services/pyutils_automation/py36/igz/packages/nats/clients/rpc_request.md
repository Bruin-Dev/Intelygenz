## Publish request message to the bus

```python
self._logger.info(f"Publishing request message to subject {topic}...")
```

* If NATS client bound to the action is not connected to NATS servers:
  ```python
  self._logger.warning(f"NATS client is disconnected from the NATS server. Resetting connection...")
  ```

  [close_nats_connections](close_nats_connections.md)

  [connect_to_nats](connect_to_nats.md)

Invoke [nats-py's `timed_request`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method

[Wait for a response](#consume-request)...

```python
self._logger.info(f"Got response message from subject {topic}")
```

## Consume request

[execute_stateful_action](../../eventbus/action/execute_stateful_action.md) is implicitly called on message arrival