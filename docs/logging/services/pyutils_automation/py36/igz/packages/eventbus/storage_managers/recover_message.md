## Recover message from Redis

```python
self._logger.info(f"Claiming message stored within Redis (payload: {msg})...")
```

* If the token to retrieve the original message is missing:
  ```python
  self._logger.exception(f'Key "token" was not found within the incoming payload {msg}')
  ```
  END

Invoke [redis' `get`](https://github.com/redis/redis-py/blob/3.3.11/redis/client.py) method

Invoke [redis' `delete`](https://github.com/redis/redis-py/blob/3.3.11/redis/client.py) method

```python
self._logger.info(f'Message successfully obtained from Redis')
```