## Relogin client

```python
logger.info(f"Relogging in host: {host} to velocloud")
```

* If the VeloCloud host is in the list of supported hosts:
    ```python
    logger.info(f"Host {host} is in the list of available clients. Refreshing authentication headers...")
    ```

    [_create_and_connect_client](_create_and_connect_client.md)