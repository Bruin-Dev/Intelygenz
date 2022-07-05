## Bouncing Check Documentation

```
self._logger.info("Looking for bouncing issues...")
```

* [Get links metrics for bouncing checks](../repositories/velocloud_repository/get_links_metrics_for_bouncing_checks.md)
* Check if link metrics is empty
    ```
    self._logger.info("List of links arrived empty while checking bouncing issues. Skipping...")
    ```
* [Get events by serial and interface](../repositories/velocloud_repository/get_events_by_serial_and_interface.md)
* [Structure link metrics](_structure_links_metrics.md)
* [Map cached edges with links metrics and contact info](_map_cached_edges_with_links_metrics_and_contact_info.md)
* for elem in metrics_with_cache_and_contact_info:
  * if not events
    ```
    self._logger.info(
                    f"No events were found for {link_status['interface']} from {serial_number} "
                    f"while looking for bouncing troubles"
                ) 
    ```
  * if are_bouncing_events_within_threshold
    ```
    self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed bouncing thresholds"
                )
    ```
  *[Process bouncing trouble](_process_bouncing_trouble.md)

```
self._logger.info("Finished looking for bouncing issues!")
```