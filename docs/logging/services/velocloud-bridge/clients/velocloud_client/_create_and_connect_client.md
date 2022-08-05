## Create and connect client

```python
logger.info(f"Logging in host: {host} to velocloud")
```

[_create_headers_by_host](_create_headers_by_host.md)

* If VeloCloud responded with valid authentication headers:
  ```python
  logger.info(f"Authentication headers refreshed for host {host} successfully")
  ```
* Otherwise:
  ```python
  logger.error(f"Authentication headers could not be refreshed for host {host}. Got response: {headers}")
  ```