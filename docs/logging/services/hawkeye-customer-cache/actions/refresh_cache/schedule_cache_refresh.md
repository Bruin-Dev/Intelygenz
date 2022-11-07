# Schedule Hawkeye Cache Refresh job

```python
logger.info(
    f"Scheduled to refresh cache every {self._config.REFRESH_CONFIG['refresh_map_minutes'] // 60} hours"
)
```

[_refresh_cache](_refresh_cache.md)

* If there's a running job to refresh the customer cache already:
  ```python
  logger.warning(
      "There is a job scheduled for refreshing the cache already. No new job is going to be scheduled."
  )
  ```
