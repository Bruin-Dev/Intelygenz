## Connect to the message bus

```python
logger.info(f"Connecting to NATS servers: {servers}...")
```

Invoke [nats-py's `connect`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method

```python
logger.info(f"Connected to NATS servers successfully")
```