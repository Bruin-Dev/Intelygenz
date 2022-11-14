## Monitor edges from a particular VeloCloud host (VCO)

```python
logger.info(f"Processing {len(host_cache)} edges in Velocloud {host}...")
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
logger.info(f"Link status with edge info from Velocloud: {links_with_edge_info}")
```

[VeloCloudRepository::group_links_by_edge](../../repositories/velocloud_repository/group_links_by_edge.md)

```python
logger.info(
    "Adding HA info to existing edges, and putting standby edges under monitoring as if they were "
    "standalone edges..."
)
```

[HARepository::map_edges_with_ha_info](../../repositories/ha_repository/map_edges_with_ha_info.md)

```python
logger.info(f"Service Outage monitoring is about to check {len(all_edges)} edges for host {host}")
logger.info(f"{len(serials_with_ha_disabled)} edges have HA disabled: {serials_with_ha_disabled}")
logger.info(f"{len(serials_with_ha_enabled)} edges have HA enabled: {serials_with_ha_enabled}")
logger.info(f"{len(primary_serials)} edges are the primary of a HA pair: {primary_serials}")
logger.info(f"{len(standby_serials)} edges are the standby of a HA pair: {standby_serials}")
```

```python
logger.info(f"Mapping cached edges with their statuses...")
```

[_map_cached_edges_with_edges_status](_map_cached_edges_with_edges_status.md)

```python
logger.info(f"Mapped cache serials with status: {mapped_serials_w_status}")
```

* For each outage type monitored:

    _Filter edges in an outage state that matches the current one_

    ```python
    logger.info(f'{outage_type.value} serials: {[e["status"]["edgeSerialNumber"] for e in down_edges]}')
    ```

    _Filter the previous set of edges to exclude any edge in Link Down (HA enabled) or Hard Down (HA enabled) state that is the standby edge of a HA pair_

    > Hard and Link Downs with HA enabled must always be documented for the primary edge in the pair

    ```python
    logger.info(
        f"{outage_type.value} serials that should be documented: "
        f'{[e["status"]["edgeSerialNumber"] for e in relevant_down_edges]}'
    )
    ```

    * If there are edges that should be documented for this outage type:
        ```python
        logger.info(f"{len(relevant_down_edges)} edges were detected in {outage_type.value} state.")
        ```
  
        _Look for edges with Business Grade link(s) down in Link Down (HA enabled) or Link Down (HA disabled) state_
  
        ```python
        logger.info(
            f"[{outage_type.value}] {len(edges_with_business_grade_links_down)} out of "
            f"{len(relevant_down_edges)} edges have at least one Business Grade link down. "
            f"Skipping the quarantine, and attempting to create tickets for all of them..."
        )
        ```
    
        * For each edge with Business Grade link(s) down:

            [_attempt_ticket_creation](_attempt_ticket_creation.md)

            * If any error takes place during the process:
              ```python
              logger.error(
                  f"[{outage_type.value}] Error while attempting ticket creation(s) for edge "
                  f"with Business Grade Link(s): {ex}"
              )
              ```

        _Look for edges in Link Down (HA enabled) or Link Down (HA disabled) state with Commercial Grade link(s) down, or in any other outage state_

        ```python
        logger.info(
            f"{len(regular_edges)} out of {len(relevant_down_edges)} have no Business Grade link(s) down. "
            f"These edges will sit in the quarantine for some time before attempting to create tickets"
        )
        ```

        [_schedule_recheck_job_for_edges](_schedule_recheck_job_for_edges.md)

    * Otherwise:
      ```python
      logger.info(
          f"No edges were detected in {outage_type.value} state. "
          f"No ticket creations will trigger for this outage type"
      )
      ```

_Look for online edges_

```python
logger.info(f'Healthy serials: {[e["status"]["edgeSerialNumber"] for e in healthy_edges]}')
```

* If there are online edges:
    ```python
    logger.info(
        f"{len(healthy_edges)} edges were detected in healthy state. Running autoresolve for all of them..."
    )
    ```

    * For each online edge:

        [_run_ticket_autoresolve_for_edge](_run_ticket_autoresolve_for_edge.md)

* Otherwise:
  ```python
  logger.info("No edges were detected in healthy state. Autoresolve won't be triggered")
  ```

```python
logger.info(f"Elapsed time processing edges in host {host}: {round((stop - start) / 60, 2)} minutes")
```