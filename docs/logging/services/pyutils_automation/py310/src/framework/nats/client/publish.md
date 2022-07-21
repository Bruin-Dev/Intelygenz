## Publish message to the bus

* If message is too large for NATS to handle (1MB+):
  ```python
  logger.warning(
      "Payload exceeds the maximum size allowed by NATS. Storing it to the external storage before "
      f"publishing to subject {subject}..."
  )
  ```
  Depending on the implementation, a call to [Redis::store](../temp_payload_storage/redis/store.md) or
  [RedisLegacy::store](../temp_payload_storage/redis_legacy/store.md) is made

```python
logger.info(f"Publishing payload to subject {subject}...")
```

Invoke [nats-py's `publish`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method

[The message will be consumed by a subscriber with interest in the subject](#consume-message-from-the-bus)

```python
logger.info(f"Payload published to subject {subject} successfully")
```

## Consume message from the bus

[_pre_recover_cb](_pre_recover_cb.md) is implicitly called on message arrival

Consume message