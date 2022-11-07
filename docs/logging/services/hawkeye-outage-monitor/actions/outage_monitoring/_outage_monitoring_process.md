## Run Hawkeye Outage Monitoring job

```python
logger.info(f"Starting Hawkeye Outage Monitor!")
```

[CustomerCacheRepository::get_cache_for_outage_monitoring](../../repositories/customer_cache_repository/get_cache_for_outage_monitoring.md)

* If response status for get Hawkeye's customer cache is not ok:
  ```python
  logger.error(
      f"Error while getting Hawkeye's customer cache: {customer_cache_response}. "
      f"Skipping outage monitoring process..."
  )
  ```
  END

[HawkeyeRepository::get_probes](../../repositories/hawkeye_repository/get_probes.md)

* If response status for get Hawkeye's devices is not ok:
  ```python
  logger.error(
      f"Error while getting Hawkeye's probes: {probes_response}. Skipping outage monitoring process..."
  )
  ```
  END

* If there are no devices to monitor:
  ```python
  logger.warning("The list of probes arrived empty. Skipping outage monitoring process...")
  ```
  END

* If there are no active devices to monitor:
  ```python
  logger.warning("All probes were detected as inactive. Skipping outage monitoring process...")
  ```
  END

[_map_probes_info_with_customer_cache](_map_probes_info_with_customer_cache.md)

_The list of devices is split to two different data sets: devices in outage state and devices online_

* If there are devices in outage state:
  ```python
  logger.info(
      f"{len(outage_devices)} devices were detected in outage state. "
      "Scheduling re-check job for all of them..."
  )
  ```
  [_schedule_recheck_job_for_devices](_schedule_recheck_job_for_devices.md)
* Otherwise:
  ```python
  logger.info("No devices were detected in outage state. Re-check job won't be scheduled")
  ```
  
* If there are devices online:
    ```python
    logger.info(
        f"{len(healthy_devices)} devices were detected in healthy state. Running autoresolve for all of them"
    )
    ```
    * For each online device:

        [_run_ticket_autoresolve](_run_ticket_autoresolve.md)

* Otherwise:
  ```python
  logger.info("No devices were detected in healthy state. Autoresolve won't be triggered")
  ```
  
```python
logger.info(f"Hawkeye Outage Monitor process finished! Took {round((stop - start) / 60, 2)} minutes")
```