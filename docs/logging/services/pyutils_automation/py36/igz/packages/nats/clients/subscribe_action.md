## Subscribe action to subject

```python
self._logger.info(
    f"Subscribing action {type(action.state_instance).__name__} to subject {topic} under NATS queue "
    f"{queue}..."
)
```

* If NATS client bound to the action is not connected to NATS servers:
  ```python
  self._logger.warning(f"NATS client is disconnected from the NATS server. Resetting connection...")
  ```

  [close_nats_connections](close_nats_connections.md)

  [connect_to_nats](connect_to_nats.md)

Invoke [nats-py's `subscribe`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method

```python
self._logger.info(
    f"Action {type(action.state_instance).__name__} subscribed to subject {topic} successfully"
)
```