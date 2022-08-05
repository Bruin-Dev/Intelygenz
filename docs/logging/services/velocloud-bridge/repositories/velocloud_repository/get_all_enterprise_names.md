## Get all enterprise names

```python
logger.info("Getting all enterprise names")
```

[get_all_enterprise_names](../../clients/velocloud_client/get_all_enterprise_names.md)

* If response status for get all enterprise names is not ok:
  ```python
  logger.error(f"Error {enterprises['status']}, error: {enterprises['body']}")
  ```