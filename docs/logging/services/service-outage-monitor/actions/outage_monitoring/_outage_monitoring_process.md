## Outage monitor process

```
self._logger.info(f"[outage_monitoring_process] Start with map cache!")
```

* [Get cache for outage monitor](../../repositories/customer_cache_repository/get_cache_for_outage_monitoring.md)
* Check if cache status is not 200

  ```
  self._logger.warning("Not found cache for service outage. Stop the outage monitoring process"
  ```

```
self._logger.info("[outage_monitoring_process] Ignoring blacklisted edges...")
```

```
self._logger.info(f"List of serials from customer cache: {serials_for_monitoring}")
self._logger.info("[outage_monitoring_process] Creating list of whitelisted serials for autoresolve...")
self._logger.info("[outage_monitoring_process] Splitting cache by host")
self._logger.info("[outage_monitoring_process] Cache split")
```

* [_process_velocloud_host](_process_velocloud_host.md)

```
self._logger.info(
            f"[outage_monitoring_process] Outage monitoring process finished! Elapsed time:"
            f"{round((stop - start) / 60, 2)} minutes"
        )
```
