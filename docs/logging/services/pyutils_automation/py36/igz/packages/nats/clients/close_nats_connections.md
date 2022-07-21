## Close NATS connections

```python
self._logger.info("Draining connections...")
```

For each subscription bound to the NATS client:
  * Invoke [nats-py's `drain`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method

```python
self._logger.info("Connections drained")
```

* If the NATS client is connected to NATS:
  ```python
  self._logger.info("Closing connection...")
  ```

  Invoke [nats-py's `close`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method

  ```python
  self._logger.info("Connection closed")
  ```