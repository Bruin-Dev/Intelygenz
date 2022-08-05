## Subject: request.enterprises.names

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get enterprise names with {json.dumps(payload)}. JSON malformed")
  ```
  END

```python
logger.info("Sending enterprise name list")
```

[get_all_enterprise_names](../repositories/velocloud_repository/get_all_enterprise_names.md)

```python
logger.info("Enterprise name list sent")
```