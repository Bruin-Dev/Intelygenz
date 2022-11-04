# Schedule Cache Refresh job

```python
logger.info(
    f"Scheduled to refresh cache every {self._config.REFRESH_CONFIG['refresh_map_minutes'] // 60} hours"
)
```

```python
logger.info(
    f"Scheduled to check if refresh is needed every "
    f"{self._config.REFRESH_CONFIG['refresh_check_interval_minutes']} minutes"
)
```

[_refresh_cache](_refresh_cache.md)

* If there's a running job to refresh the customer caches already:
  ```python
  logger.warning(
      f"There is a job scheduled for refreshing the cache already. No new job is going to be scheduled."
  )
  ```
