## Run Service Affecting Monitoring job

```python
logger.info(f"Starting Service Affecting Monitor process now...")
```

* If response status for get VeloCloud's customer cache is not ok:
  ```python
  logger.error(
      f"Error while getting VeloCloud's customer cache: {customer_cache_response}. "
      f"Skipping Service Affecting monitoring process..."
  )
  ```
  END

[CustomerCacheRepository::get_cache_for_affecting_monitoring](../../repositories/customer_cache_repository/get_cache_for_affecting_monitoring.md)

* If the cache of customers is empty:
  ```python
  logger.warning("Got an empty customer cache. Skipping Service Affecting monitoring process...")
  ```
  END

[_latency_check](_latency_check.md)

[_packet_loss_check](_packet_loss_check.md)

[_jitter_check](_jitter_check.md)

[_bandwidth_check](_bandwidth_check.md)

[_bouncing_check](_bouncing_check.md)

[_run_autoresolve_process](_run_autoresolve_process.md)

```python
logger.info(f"Finished processing all links! Took {round((time.time() - start_time) / 60, 2)} minutes")
```