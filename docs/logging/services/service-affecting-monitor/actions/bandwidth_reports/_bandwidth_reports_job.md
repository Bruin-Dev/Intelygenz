## Run Daily Bandwidth Report job

```python
logger.info(f"[bandwidth-reports] Running bandwidth reports process for {len(clients)} client(s)")
```

[CustomerCacheRepository::get_cache](../../repositories/customer_cache_repository/get_cache.md)

* If response status for get customer cache is not ok:
  ```python
  logger.error("[bandwidth-reports] Error getting customer cache. Process cannot keep going.")
  ```
  END

```python
logger.info(f"[bandwidth-reports] Creating enterprise id edge id_relation list")
```

[VelocloudRepository::get_links_metrics_by_host](../../repositories/velocloud_repository/get_links_metrics_by_host.md)

* If response status for get links metrics by VeloCloud host (VCO) is not ok:
  ```python
  logger.error("[bandwidth-reports] Error getting links metrics. Process cannot keep going.")
  ```
  END

* For each client that should receive this report:

  [_generate_bandwidth_report_for_client](_generate_bandwidth_report_for_client.md)

  ```python
  logger.info(f"[bandwidth-reports] Generating bandwidth report for client id {client_id} and client name {client_name}")
  ```
  
  [_add_bandwitdh_to_links_metrics](_add_bandwidth_to_links_metrics.md)  

  [prepare_items_for_bandwidth_report](prepare_items_for_bandwidth_report.md)
  
  * If something fails:
  ```python
  logger.error(f"[bandwidth-reports] No report for client {client_id} was sent via email")
  ```

```python
logger.info(
    f"[bandwidth-reports] Report generation for all clients finished. "
    f"Took {round((bandwidth_report_end_time - bandwidth_report_init_time).total_seconds() / 60, 2)} minutes."
)
```