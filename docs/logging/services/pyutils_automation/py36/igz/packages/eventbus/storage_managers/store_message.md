## Store message to Redis

```python
self._logger.info(f'Storing message within Redis...')
```

Invoke [redis' `set`](https://github.com/redis/redis-py/blob/3.3.11/redis/client.py) method

```python
self._logger.info(f'Message successfully stored within Redis')
```