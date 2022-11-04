## Subject: customer.cache.get

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get customer cache using {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `filter` filter with a list of VCOs to get caches for:
  ```python
  logger.error(f'Cannot get customer cache info using {json.dumps(body)}. Need "filter"')
  ```
  END

[StorageRepository::get_host_cache](../../repositories/storage_repository/get_host_cache.md)

* If no cache could be found for the list of VCOs specified in the filter:
  ```python
  logger.warning(f'Cache is still being built for host(s): {", ".join(body["filter"].keys())}')
  ```
  END

* If `last_contact_filter` was specified and no cached edges were last contacted before the last contact date:
  ```python
  logger.warning(f"No edges were found for the specified filters: {body}")
  ```
  END

```python
logger.info(f"{len(filter_cache)} edges were found for the specified filters: {body}")
```

```python
logger.info(f"Get customer response published in event bus")
```
