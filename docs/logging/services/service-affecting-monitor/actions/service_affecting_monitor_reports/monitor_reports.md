## Run Reoccurring Trouble Reports job

```python
logger.info(f"Starting Reoccurring Trouble Reports job for host {host} and clients {clients_id}")
```

[CustomerCacheRepository::get_cache](../../repositories/customer_cache_repository/get_cache.md)

* If cache of customers is empty:
  ```python
  logger.error("[service-affecting-monitor-reports] Got an empty customer cache. Process cannot keep going.")
  ```
  END

* For each client that should receive this report:
  ```python
  logger.info(f"Getting Service Affecting ticket for client {client_id}...")
  ```

  [BruinRepository::get_affecting_ticket_for_report](../../repositories/bruin_repository/get_affecting_ticket_for_report.md)

  * If no Service Affecting tickets were found:
    ```python
    msg = (
        f"No Service Affecting tickets were found for client {client_id}. A report claiming "
        f"that no data matching the criteria was found will be delivered soon."
    )
    logger.warning(msg)
    ```
  * Otherwise:
    ```python
    logger.info(f"Got Service Affecting ticket for client {client_id}!")
    ```

[_service_affecting_monitor_report](_service_affecting_monitor_report.md)

```python
logger.info(
    f"[service-affecting-monitor-reports] Reports generation finished. "
    f"Took {round((monitor_report_end_time - monitor_report_init_time).total_seconds() / 60, 2)} minutes."
)
```