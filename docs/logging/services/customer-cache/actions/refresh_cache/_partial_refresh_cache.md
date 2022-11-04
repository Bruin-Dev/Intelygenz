## Refresh customer cache for a VCO

```python
logger.info(f"Filtering the list of edges for host {host}")
```

* For each edge in the VCO:

    [_filter_edge_list](_filter_edge_list.md)

```python
logger.info(f"Finished filtering edges for host {host}")
```

```python
logger.info(f"Adding {len(ha_serials)} HA edges as standalone edges to cache of host {host}...")
```

[_add_ha_devices_to_cache](_add_ha_devices_to_cache.md)

```python
logger.info(f"Finished adding HA edges to cache of host {host}")
```

* If resulting cache is empty after crossing VeloCloud and Bruin data for each edge:
  ```python
  error_msg = (
      f"Cache for host {host} was empty after cross referencing with Bruin."
      f" Check if Bruin is returning errors when asking for management statuses of the host"
  )
  logger.error(error_msg)
  ```
  END

[StorageRepository::get_cache](../../repositories/storage_repository/get_cache.md)

```python
logger.info(
    f"Crossing currently stored cache ({len(stored_cache)} edges) with new one ({len(cache)} edges)..."
)
```

_Both caches are merged_

```python
logger.info(f"Crossed cache of host {host} has {len(crossed_cache)} edges")
```

```python
logger.info(f"Removing {len(self._invalid_edges[host])} invalid edges from crossed cache of host {host}...")
```

_Edges whose data from Bruin could not be fetched are removed from the cache before saving it_

```python
logger.info(f"Invalid edges removed from cache! Final cache has {len(final_cache)} edges")
```

```python
logger.info(f"Storing cache of {len(final_cache)} edges to Redis for host {host}")
```

[StorageRepository::set_cache](../../repositories/storage_repository/set_cache.md)

[_send_email_snapshot](_send_email_snapshot.md)

```python
logger.info(f"Finished storing cache for host {host}")
```