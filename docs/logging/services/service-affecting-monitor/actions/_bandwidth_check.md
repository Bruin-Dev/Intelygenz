## Bandwidth Check Documentation

```
self._logger.info("Looking for bandwidth issues...")
```

* [Get links metrics for bandwidth checks](../repositories/velocloud_repository/get_links_metrics_for_bandwidth_checks.md)
* Check if link metrics is empty
    ```
    self._logger.info("List of links arrived empty while checking bandwidth issues. Skipping...")
    ```
* [Structure link metrics](_structure_links_metrics.md)
* [Map cached edges with links metrics and contact info](_map_cached_edges_with_links_metrics_and_contact_info.md)
* for elem in metrics_with_cache_and_contact_info:
  * if within_threshold
    ```
    self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed any bandwidth thresholds"
                )
    ```
  *[Process bandwidth trouble](_process_bandwidth_trouble.md)

```
self._logger.info("Finished looking for bandwidth issues!")
```