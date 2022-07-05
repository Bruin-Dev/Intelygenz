## Packet loss Check Documentation

```
self._logger.info("Looking for packet loss issues...")
```

* [Get links metrics for packet loss checks](../repositories/velocloud_repository/get_links_metrics_for_packet_loss_checks.md)
* Check if link metrics is empty
    ```
    self._logger.info("List of links arrived empty while checking packet loss issues. Skipping...")
    ```
* [Structure link metrics](_structure_links_metrics.md)
* [Map cached edges with links metrics and contact info](_map_cached_edges_with_links_metrics_and_contact_info.md)
* for elem in metrics_with_cache_and_contact_info:
  * if are_packet_loss_metrics_within_threshold
    ```
    self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed packet loss thresholds"
                )
    ```
  *[Process packet loss trouble](_process_packet_loss_trouble.md)

```
self._logger.info("Finished looking for packet loss issues!")
```