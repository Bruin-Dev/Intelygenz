## Check links for Packet Loss issues

```python
logger.info("Looking for packet loss issues...")
```

[VelocloudRepository::get_links_metrics_for_packet_loss_checks](../../repositories/velocloud_repository/get_links_metrics_for_packet_loss_checks.md)

* If no metrics were found:
  ```python
  logger.warning("List of links arrived empty while checking packet loss issues. Skipping...")
  ```
  END

[_structure_links_metrics](_structure_links_metrics.md)

[_map_cached_edges_with_links_metrics_and_contact_info](_map_cached_edges_with_links_metrics_and_contact_info.md)

* For each link:

    * If Packet Loss metrics are within thresholds:
      ```python
      logger.info(
          f"Link {link_status['interface']} from {serial_number} didn't exceed packet loss thresholds"
      )
      ```
      _Continue with next link_
    * Otherwise:

        [_process_packet_loss_trouble](_process_packet_loss_trouble.md)

```python
logger.info("Finished looking for packet loss issues!")
```