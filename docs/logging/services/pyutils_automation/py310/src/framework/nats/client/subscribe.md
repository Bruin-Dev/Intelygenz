## Publish message to the bus

```python
logger.info(f"Subscribing to subject {subject} with queue group {queue}...")
```

_Invoke [nats-py's `subscribe`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method_

```python
logger.info(f"Subscribed to subject successfully")
```