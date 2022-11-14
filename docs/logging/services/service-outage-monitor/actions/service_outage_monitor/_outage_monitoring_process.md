## Run Service Outage Monitoring job

```python
logger.info(f"Starting Service Outage Monitor process now...")
```

[CustomerCacheRepository::get_cache_for_outage_monitoring](../../repositories/customer_cache_repository/get_cache_for_outage_monitoring.md)

* If response status for get VeloCloud's customer cache is not ok:
  ```python
  logger.error(
      f"Error while getting VeloCloud's customer cache: {customer_cache_response}. "
      f"Skipping Service Outage monitoring process..."
  )
  ```
  END

```python
logger.info(f"Got customer cache with {len(cache)} monitorable edges")
```

```python
logger.info("Ignoring blacklisted edges...")
```

_Blacklisted edges are filtered out_

```python
logger.info(f"Got {len(cache)} monitorable edges after filtering out blacklisted ones")
```

```python
logger.info(f"Monitorable serials: {serials_for_monitoring}")
```

```python
logger.info("Creating list of whitelisted serials for auto-resolve...")
```

* If the auto-resolve whitelist is disabled / empty:
  ```python
  logger.info("Auto-resolve whitelist is not enabled, so all edges will be monitored")
  ```
* Otherwise:
  ```python
  logger.info(f"Got {len(self._autoresolve_serials_whitelist)} edges whitelisted for auto-resolves")
  ```

```python
logger.info("Splitting cache by VeloCloud host")
```

_Cache of customers is split by VeloCloud host (VCO)_

```python
logger.info("Cache split")
```

* For each VCO under monitoring:

    [_process_velocloud_host](_process_velocloud_host.md)

```python
logger.info(
    f"[outage_monitoring_process] Outage monitoring process finished! Elapsed time:"
    f"{round((stop - start) / 60, 2)} minutes"
)
```