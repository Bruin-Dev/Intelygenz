## Store message to Redis (legacy style)

```python
logger.info(f"Storing payload of {len(payload)} bytes under Redis key {token}")
```

Invoke [redis' `set`](https://github.com/redis/redis-py/blob/3.3.11/redis/client.py) method

```python
logger.info(f"Payload stored under Redis key {token} retrieved successfully")
```