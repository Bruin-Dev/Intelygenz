## Subject: hawkeye.customer.cache.get

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get customer cache using {json.dumps(payload)}. JSON malformed")
  ```
  END

[StorageRepository::get_hawkeye_cache](../../repositories/storage_repository/get_hawkeye_cache.md)

* If no cache could be found:
  ```python
  logger.warning(f"Cache is still being built")
  ```
  END

* If `last_contact_filter` was specified and no cached devices were last contacted before the last contact date:
  ```python
  logger.warning(f"No devices were found for the specified filters: {body}")
  ```
  END

```python
logger.info(f"{len(filter_cache)} devices were found for the specified filters: {body}")
```

```python
logger.info(f"Get customer response published in event bus")
```
