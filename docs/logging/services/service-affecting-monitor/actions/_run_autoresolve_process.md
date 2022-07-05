## Run autoresolve process Documentation

```
self._logger.info("Starting auto-resolve process...")
```
* [Get links metrics for autoresolve](../repositories/velocloud_repository/get_links_metrics_for_autoresolve.md)

* if link metrics is empty
  ```
  self._logger.info("List of links metrics arrived empty while running auto-resolve process. Skipping...")  
  ```
* [Get events by serial and interface](../repositories/velocloud_repository/get_events_by_serial_and_interface.md)
* [Structure link metrics](_structure_links_metrics.md)
* [Map cached edges with links metrics and contact info](_map_cached_edges_with_links_metrics_and_contact_info.md)

```
self._logger.info(f"Running auto-resolve for {len(edges_with_links_info)} edges")
```

autoresolve_tasks = [[Run autoresolve for edge](_run_autoresolve_for_edge.md) for edge in edges_with_links_info]

```
self._logger.info("Auto-resolve process finished!")
```