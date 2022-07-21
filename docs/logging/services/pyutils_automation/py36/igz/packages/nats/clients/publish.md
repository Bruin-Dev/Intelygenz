## Publish message to the bus

```python
self._logger.info(f"Publishing message to subject {topic}...")
```

* If NATS client bound to the action is not connected to NATS servers:
  ```python
  self._logger.warning(f"NATS client is disconnected from the NATS server. Resetting connection...")
  ```

  [close_nats_connections](close_nats_connections.md)

  [connect_to_nats](connect_to_nats.md)

Invoke [nats-py's `publish`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method

[The message will be consumed by a subscriber with interest in the subject.](#consume-message-from-the-bus)

```python
self._logger.info(f"Message published to subject {topic} successfully")
```

## Consume message from the bus

[execute_stateful_action](../../eventbus/action/execute_stateful_action.md) is implicitly called on message arrival
