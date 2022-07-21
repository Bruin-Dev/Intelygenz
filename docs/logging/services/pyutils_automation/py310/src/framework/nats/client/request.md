## Publish request message to the bus

```python
logger.info(f"Requesting a response from subject {subject}...")
```

Invoke [nats-py's `request`](https://github.com/nats-io/nats.py/blob/main/nats/aio/client.py) method, which internally
calls [publish](publish.md)

[Wait for a response](#consume-request)...

```python
logger.info(f"Response received from a replier subscribed to subject {subject}")
```

* If response message is stored to an external storage:
  ```python
  logger.warning(
      f"Response received from subject {subject} exceeds the maximum size allowed by NATS. Recovering it "
      "from the external storage..."
  )
  ```
  Depending on the implementation, a call to [Redis::recover](../temp_payload_storage/redis/recover.md) or
  [RedisLegacy::recover](../temp_payload_storage/redis_legacy/recover.md) is made

## Consume request

[_pre_recover_cb](_pre_recover_cb.md) is implicitly called on request message arrival

Consume message

Invoke [nats-py's `respond`](https://github.com/nats-io/nats.py/blob/main/nats/aio/msg.py) method with the response
message, which internally calls [publish](publish.md)