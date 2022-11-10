## Check links for Latency issues

```python
logger.info("Looking for latency issues...")
```

[VelocloudRepository::get_links_metrics_for_latency_checks](../../repositories/velocloud_repository/get_links_metrics_for_latency_checks.md)

* If no metrics were found:
  ```python
  logger.warning("List of links arrived empty while checking latency issues. Skipping...")
  ```
  END

[_structure_links_metrics](_structure_links_metrics.md)

[_map_cached_edges_with_links_metrics_and_contact_info](_map_cached_edges_with_links_metrics_and_contact_info.md)

* For each link:

    * If Latency metrics are within thresholds:
      ```python
      logger.info(f"Link {link_status['interface']} from {serial_number} didn't exceed latency thresholds")
      ```
      _Continue with next link_
    * Otherwise:

        [_process_latency_trouble](_process_latency_trouble.md)

```python
logger.info("Finished looking for latency issues!")
```