## Map edges with their HA info

* For each edge:
    * If HA is not enabled for the edge:
      ```python
      logger.info(f"No HA info was found for edge {serial_number}. Skipping...")
      ```
      _Continue with next edge_

    * If the state of the standby edge linked to this edge (primary) is READY or FAILED:
      ```python
      logger.info(f"HA partner for {serial_number} is in state {ha_state}. Mapping HA info to edge...")
      ```
    * Otherwise:
      ```python
      logger.warning(
          f"HA partner for {serial_number} is in state {ha_state}, so HA will be considered as disabled for "
          "this edge"
      )
      ```