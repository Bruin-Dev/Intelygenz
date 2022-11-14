## Re-check edges sitting in the quarantine

```python
logger.info(
    f"[{outage_type.value}] Re-checking {len(outage_edges)} edges in outage state prior to ticket creation..."
)
```

```python
logger.info(f"[{outage_type.value}] Edges in outage before quarantine recheck: {outage_edges}")
```

[VelocloudRepository::get_links_with_edge_info](../../repositories/velocloud_repository/get_links_with_edge_info.md)

* If response status for get links with edge info is not ok:
  ```python
  logger.error(
      f"Error while getting links with edge info for VeloCloud host {host}: {links_with_edge_info_response}. "
      f"Skipping monitoring process for this host..."
  )
  ```
  END

[VelocloudRepository::get_network_enterprises](../../repositories/velocloud_repository/get_network_enterprises.md)

* If response status for get network enterprises is not ok:
  ```python
  logger.error(
      f"Error while getting network enterprises for VeloCloud host {host}: {network_enterprises_response}. "
      f"Skipping monitoring process for this host..."
  )
  ```
  END

```python
logger.info(
    f"[{outage_type.value}] Velocloud edge status response in quarantine recheck: "
    f"{links_with_edge_info_response}"
)
```

[VeloCloudRepository::group_links_by_edge](../../repositories/velocloud_repository/group_links_by_edge.md)

```python
logger.info(
    f"[{outage_type.value}] Adding HA info to existing edges, and putting standby edges under monitoring as if "
    "they were standalone edges..."
)
```

[HARepository::map_edges_with_ha_info](../../repositories/ha_repository/map_edges_with_ha_info.md)

[_map_cached_edges_with_edges_status](_map_cached_edges_with_edges_status.md)

```python
logger.info(f"[{outage_type.value}] Current status of edges that were in outage state: {edges_full_info}")
```

```python
logger.info(f"[{outage_type.value}] Edges still in outage state after recheck: {edges_still_down}")
logger.info(f"[{outage_type.value}] Serials still in outage state after recheck: {serials_still_down}")
logger.info(f"[{outage_type.value}] Edges that are healthy after recheck: {healthy_edges}")
logger.info(f"[{outage_type.value}] Serials that are healthy after recheck: {healthy_serials}")
```

* If there are still edges in outage state:
    ```python
    logger.info(
        f"[{outage_type.value}] {len(edges_still_down)} edges are still in outage state after re-check. "
        "Attempting outage ticket creation for all of them..."
    )
    ```

    * For each edge in outage state:

        [_attempt_ticket_creation](_attempt_ticket_creation.md)

        * If any error takes place during the process:
          ```python
          logger.error(
               f"[{outage_type.value}] Error while attempting ticket creation(s) for edge in "
              f"the quarantine: {ex}"
          )
          ```

* Otherwise:
  ```python
  logger.info(
      f"[{outage_type.value}] No edges were detected in outage state after re-check. "
      "Outage tickets won't be created"
  )
  ```

* If there are edges back online:
    ```python
    logger.info(
        f"[{outage_type.value}] {len(healthy_edges)} edges were detected in healthy state after re-check. '"
        "Running autoresolve for all of them..."
    )
    logger.info(f"[{outage_type.value}] Edges that are going to be attempted to autoresolve: {healthy_edges}")
    ```

    * For each online edge:

        [_run_ticket_autoresolve_for_edge](_run_ticket_autoresolve_for_edge.md)

* Otherwise:
  ```python
  logger.info(
      f"[{outage_type.value}] No edges were detected in healthy state. Autoresolve won't be triggered"
  )
  ```

```python
logger.info(f"[{outage_type.value}] Re-check process finished for {len(outage_edges)} edges")
```