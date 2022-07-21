## Recover message to Redis (new style)

```python
logger.info(f"Retrieving payload stored under Redis key {token}...")
```

Invoke [redis' `get`](https://github.com/redis/redis-py/blob/3.3.11/redis/client.py) method

```python
logger.info(f"Payload stored under Redis key {key} successfully")
```