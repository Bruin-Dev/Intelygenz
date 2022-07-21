## Connect all consumers and producers to the message bus

```python
self._logger.info(f"Establishing connection to NATS for all consumers...")
```

For all consumers attached to the event bus: 
  * [connect_to_nats](../../nats/clients/connect_to_nats.md)

```python
self._logger.info(f"Connection to NATS established successfully for all consumers")
```

* If there is a producer attached to the event bus:
  ```python
  self._logger.info(f"Establishing connection to NATS for producer...")
  ```

  [connect_to_nats](../../nats/clients/connect_to_nats.md)

  ```python
  self._logger.info(f"Connection to NATS established successfully for producer")
  ```