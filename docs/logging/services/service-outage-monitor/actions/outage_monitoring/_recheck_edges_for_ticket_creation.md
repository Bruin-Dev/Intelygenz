## Recheck edges for ticket creation
```
self._logger.info(f"[{outage_type.value}] Re-checking {len(outage_edges)} edges in outage state prior to ticket creation...")
self._logger.info(f"[{outage_type.value}] Edges in outage before quarantine recheck: {outage_edges}")
```
* [get_links_with_edge_info](../../repositories/velocloud_repository/get_links_with_edge_info.md)
* If get links with edge info status not Ok:
  ```
  self._logger.warning(f"Bad status calling to get links with edge info for host: {host}. Skipping recheck ...")
  ```
* [get_network_enterprises](../../repositories/velocloud_repository/get_network_enterprises.md)
* If get network enterprises tatus not Ok:
  ```
  self._logger.warning(f"Bad status calling to get network enterprises info for host: {host}. Skipping recheck ...")
  ```    
```
self._logger.info(f"[{outage_type.value}] Velocloud edge status response in quarantine recheck: "
                    f"{links_with_edge_info_response}")
```  
* [group_links_by_edge](../../repositories/velocloud_repository/group_links_by_edge.md)
```
self._logger.info(f"[{outage_type.value}] Adding HA info to existing edges, and putting standby edges under monitoring as if "
            "they were standalone edges...")
``` 
* [map_edges_with_ha_info](../../repositories/ha_repository/map_edges_with_ha_info.md)
* [get_edges_with_standbys_as_standalone_edges](../../repositories/ha_repository/get_edges_with_standbys_as_standalone_edges.md)
* [_map_cached_edges_with_edges_status](_map_cached_edges_with_edges_status.md)
```
self._logger.info(f"[{outage_type.value}] Current status of edges that were in outage state: {edges_full_info}")
self._logger.info(f"[{outage_type.value}] Edges still in outage state after recheck: {edges_still_down}")
self._logger.info(f"[{outage_type.value}] Serials still in outage state after recheck: {serials_still_down}")
self._logger.info(f"[{outage_type.value}] Edges that are healthy after recheck: {healthy_edges}")
self._logger.info(f"[{outage_type.value}] Serials that are healthy after recheck: {healthy_serials}")
``` 
* If edges still down:
  ```
  self._logger.info(f"[{outage_type.value}] {len(edges_still_down)} edges are still in outage state after re-check. "
                "Attempting outage ticket creation for all of them...")
  ``` 
  * If environment PRODUCTION:
    * [_attempt_ticket_creation](_attempt_ticket_creation.md)
    * If error in attempt ticket creation:
      ```
      self._logger.error(f"[{outage_type.value}] Error while attempting ticket creation(s) for edge in "
                         f"the quarantine: {ex}")
      ``` 
  * Else:
    ```
    self._logger.info(f"[{outage_type.value}] Not starting outage ticket creation for {len(edges_still_down)} faulty "
                      f"edges because the current working environment is {working_environment.upper()}.")
    ``` 
* Else:
  ```
  self._logger.info(f"[{outage_type.value}] No edges were detected in outage state after re-check. "
              "Outage tickets won't be created")
  ``` 
* If healthy edges:
  ```
  self._logger.info(
                f"[{outage_type.value}] {len(healthy_edges)} edges were detected in healthy state after re-check. '"
                "Running autoresolve for all of them..."
            )
  self._logger.info(
                f"[{outage_type.value}] Edges that are going to be attempted to autoresolve: {healthy_edges}"
            )
  ``` 
  * [_run_ticket_autoresolve_for_edge](_run_ticket_autoresolve_for_edge.md)
* Else:
  ```
  self._logger.info(
                f"[{outage_type.value}] No edges were detected in healthy state. " "Autoresolve won't be triggered"
            )
  ``` 
```
self._logger.info(f"[{outage_type.value}] Re-check process finished for {len(outage_edges)} edges")
``` 