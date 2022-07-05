## Process velocloud host Documentation

```
self._logger.info(f"Processing {len(host_cache)} edges in Velocloud {host}...")
```

* [get_link_with_edge_info](../../repositories/velocloud_repository/get_links_with_edge_info.md)
* If status get link with edge info not OK:
  ```
  self._logger.warning(f"Not found links with edge info for host: {host}. Stop process velocloud host")
  ```
* [get_network_enterprises](../../repositories/velocloud_repository/get_network_enterprises.md)
* If status get network enterprises not OK:
  ```
  self._logger.warning(f"Not found network enterprises for host: {host}. Stop process velocloud host")
  ```
```
self._logger.warning(f"Link status with edge info from Velocloud: {links_with_edge_info}")
```
* [grouped_links_by_edge](../../repositories/velocloud_repository/group_links_by_edge.md)
```
self._logger.info(
            "Adding HA info to existing edges, and putting standby edges under monitoring as if they were "
            "standalone edges..."
        )
```
* [map_edges_with_ha_info](../../repositories/ha_repository/map_edges_with_ha_info.md)
```
self._logger.info(f"Service Outage monitoring is about to check {len(all_edges)} edges")
self._logger.info(f"{len(serials_with_ha_disabled)} edges have HA disabled: {serials_with_ha_disabled}")
self._logger.info(f"{len(serials_with_ha_enabled)} edges have HA enabled: {serials_with_ha_enabled}")
self._logger.info(f"{len(primary_serials)} edges are the primary of a HA pair: {primary_serials}")
self._logger.info(f"{len(standby_serials)} edges are the standby of a HA pair: {standby_serials}")
```
* [map_cached_edges_with_edges_status](_map_cached_edges_with_edges_status.md)
```
self._logger.info(f"Mapped cache serials with status: {mapped_serials_w_status}")
```
* For outage in outages:
  ```
  self._logger.info(f'{outage_type.value} serials: {[e["status"]["edgeSerialNumber"] for e in down_edges]}')
  self._logger.info(
                f"{outage_type.value} serials that should be documented: "
                f'{[e["status"]["edgeSerialNumber"] for e in relevant_down_edges]}'
            )
  ```
  * If relevant down edges:
    ```
    self._logger.info(f"{len(relevant_down_edges)} edges were detected in {outage_type.value} state.")
    ```
    * [attempt_ticket_creation](_attempt_ticket_creation.md)
    * If ticket creation None:
      ```
      self._logger.error(f"[{outage_type.value}] Error while attempting ticket creation(s) for edge "
                         f"with Business Grade Link(s): {ex}")
      ```
    * [_schedule_recheck_job_for_edges](_schedule_recheck_job_for_edges.md)
  * Else:
    ```
    self._logger.info(
                    f"No edges were detected in {outage_type.value} state. "
                    f"No ticket creations will trigger for this outage type"
                )
    ```
```
self._logger.info(f'Healthy serials: {[e["status"]["edgeSerialNumber"] for e in healthy_edges]}')
```
* IF healthy edges:
  ```
  self._logger.info(
                f"{len(healthy_edges)} edges were detected in healthy state. Running autoresolve for all of them..."
            )
  ```
  * [_run_ticket_autoresolve_for_edge](_run_ticket_autoresolve_for_edge.md)
* Else:
  ```
  self._logger.info(
                "No edges were detected in healthy state. Autoresolve won't be triggered"
            )
  ```
```
self._logger.info(f"Elapsed time processing edges in host {host}: {round((stop - start) / 60, 2)} minutes")
```