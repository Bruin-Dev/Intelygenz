## Connect to the messages bus

```python
self._logger.info(f"Connecting client to NATS servers: {self._config['servers']}...")
```

Invoke [nats-py's `connect`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method

```python
self._logger.info(f"Connected to NATS servers successfully")
```