## Run Auto-Resolve for tickets related to edges whose links have stabilized

```python
logger.info("Starting auto-resolve process...")
```

[VelocloudRepository::get_links_metrics_for_autoresolve](../../repositories/velocloud_repository/get_links_metrics_for_autoresolve.md)

* If no metrics were found:
  ```python
  logger.warning("List of links metrics arrived empty while running auto-resolve process. Skipping...")
  ```
  END

[VelocloudRepository::get_events_by_serial_and_interface](../../repositories/velocloud_repository/get_events_by_serial_and_interface.md)

[_structure_links_metrics](_structure_links_metrics.md)

[_map_cached_edges_with_links_metrics_and_contact_info](_map_cached_edges_with_links_metrics_and_contact_info.md)

_Links are grouped by edge_

* For each edge:

    [_run_autoresolve_for_edge](_run_autoresolve_for_edge.md)

```python
logger.info("Auto-resolve process finished!")
```