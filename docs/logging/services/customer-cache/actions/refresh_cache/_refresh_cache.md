# Run Customer Cache Refresh job

[_need_to_refresh_cache](_need_to_refresh_cache.md)

* If the cache refresh is not due yet:
  ```python
  logger.info("Cache refresh is not due yet. Skipping refresh process...")
  ```
  END

```python
logger.info("Starting job to refresh the cache of edges...")
```

```python
logger.info(f"Velocloud hosts that are going to be cached: {', '.join(velocloud_hosts)}")
```

```python
logger.info("Claiming edges for the hosts specified in the config...")
```

[VelocloudRepository::get_all_velo_edges](../../repositories/velocloud_repository/get_all_velo_edges.md)

* If no edges could be retrieved:
    ```python
    logger.warning(
        f"Got an empty list of edges for hosts {', '.join(velocloud_hosts)} from VeloCloud. "
        f"Retrying to get edges..."
    )
    ```
  
    * If the attempts' threshold to retry retrieving edges across VCOs has not been maxed out yet:
      ```python
      logger.warning(f"Couldn't find any edge to refresh the cache. Re-trying job...")
      ```
      _The Customer Cache Refresh job triggers immediately again_
    * Otherwise:
      ```python
      error_message = (
          "Too many consecutive failures happened while trying "
          "to claim the list of edges from Velocloud"
      )
      raise Exception(error_message)
      ...
      logger.error(f"An error occurred while refreshing the cache -> {e}")
      ```
      END

```python
logger.info(f"Distinguishing {len(edge_list)} edges per Velocloud host...")
```

```python
logger.info("Refreshing cache for each of the hosts...")
```

* For each VCO whose cache needs a refresh:

    [_partial_refresh_cache](_partial_refresh_cache.md)

[StorageRepository::update_refresh_date](../../repositories/storage_repository/update_refresh_date.md)

[_send_email_multiple_inventories](_send_email_multiple_inventories.md)

```python
logger.info("Finished refreshing cache!")
```