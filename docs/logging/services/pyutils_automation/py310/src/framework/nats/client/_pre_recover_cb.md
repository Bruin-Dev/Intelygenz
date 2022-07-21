# Recover message before consuming it

* If message is stored to an external storage:
  ```python
  logger.warning(
      f"Message received in subject {msg.subject} exceeds the maximum size allowed by NATS. Recovering "
      "it from the external storage..."
  )
  ```
  Depending on the implementation, a call to [Redis::recover](../temp_payload_storage/redis/recover.md) or
  [RedisLegacy::recover](../temp_payload_storage/redis_legacy/recover.md) is made