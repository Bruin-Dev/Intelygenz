## Latency Check Documentation

```
self._logger.info("Looking for latency issues...")
```

* [Get links metrics for latency checks](../repositories/velocloud_repository/get_links_metrics_for_latency_checks.md)
* Check if link metrics is empty
    ```
    self._logger.info("List of links arrived empty while checking latency issues. Skipping...")
    ```
* [Structure link metrics](_structure_links_metrics.md)
* [Map cached edges with links metrics and contact info](_map_cached_edges_with_links_metrics_and_contact_info.md)
* for elem in metrics_with_cache_and_contact_info:
  * if are_latency_metrics_within_threshold
    ```
    self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed latency thresholds"
                )
    ```
  *[Process latency trouble](_process_latency_trouble.md)

```
self._logger.info("Finished looking for latency issues!")
```