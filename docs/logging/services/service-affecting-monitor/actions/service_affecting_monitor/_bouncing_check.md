## Check links for Circuit Instability issues

```python
logger.info("Looking for bouncing issues...")
```

[VelocloudRepository::get_links_metrics_for_bouncing_checks](../../repositories/velocloud_repository/get_links_metrics_for_bouncing_checks.md)

* If no metrics were found:
  ```python
  logger.warning("List of links arrived empty while checking bouncing issues. Skipping...")
  ```
  END

[VelocloudRepository::get_events_by_serial_and_interface](../../repositories/velocloud_repository/get_events_by_serial_and_interface.md)

[_structure_links_metrics](_structure_links_metrics.md)

[_map_cached_edges_with_links_metrics_and_contact_info](_map_cached_edges_with_links_metrics_and_contact_info.md)

* For each link:

    * If no VeloCloud events could be found this link:
      ```python
      logger.warning(
          f"No events were found for {link_status['interface']} from {serial_number} "
          f"while looking for bouncing troubles"
      )
      ```
      _Continue with next link_

    * If Circuit Instability metrics are within thresholds:
      ```python
      logger.info(f"Link {link_status['interface']} from {serial_number} didn't exceed bouncing thresholds")
      ```
      _Continue with next link_
    * Otherwise:

        [_process_bouncing_trouble](_process_bouncing_trouble.md)

```python
logger.info("Finished looking for bouncing issues!")
```