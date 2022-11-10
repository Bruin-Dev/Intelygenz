## Check links for Bandwidth Over-Utilization issues

```python
logger.info("Looking for bandwidth issues...")
```

[VelocloudRepository::get_links_metrics_for_bandwidth_checks](../../repositories/velocloud_repository/get_links_metrics_for_bandwidth_checks.md)

* If no metrics were found:
  ```python
  logger.warning("List of links arrived empty while checking bandwidth issues. Skipping...")
  ```
  END

[_structure_links_metrics](_structure_links_metrics.md)

[_map_cached_edges_with_links_metrics_and_contact_info](_map_cached_edges_with_links_metrics_and_contact_info.md)

* For each link:

    * If Bandwidth Over-Utilization troubles are not enabled for the customer than owns this link:
      ```python
      logger.warning(f"Bandwidth checks are not enabled for client {client_id}. Skipping...")
      ```
      _Continue with next link_

    * If Bandwidth Over-Utilization metrics are within thresholds:
      ```python
      logger.info(
          f"Link {link_status['interface']} from {serial_number} didn't exceed any bandwidth thresholds"
      )
      ```
      _Continue with next link_
    * Otherwise:

        [_process_bandwidth_trouble](_process_bandwidth_trouble.md)

```python
logger.info("Finished looking for bandwidth issues!")
```