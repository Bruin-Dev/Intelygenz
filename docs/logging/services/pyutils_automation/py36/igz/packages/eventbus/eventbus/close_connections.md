## Close connections for all consumers

```python
self._logger.info("Closing connection for all consumers in the event bus...")
```

For each consumer in the event bus:
  * [close_nats_connections](../../nats/clients/close_nats_connections.md)

```python
self._logger.info("Connections closed for all consumers in the event bus")
```

* If there is a producer attached to the event bus:
  ```python
  self._logger.info("Closing connection for producer in the event bus...")
  ```

  [close_nats_connections](../../nats/clients/close_nats_connections.md)

  ```python
  self._logger.info("Closed connection for producer in the event bus")
  ```