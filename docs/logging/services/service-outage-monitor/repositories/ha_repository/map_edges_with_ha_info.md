## Map edges with HA info Documentation
* for edge in edges
  * If not edge ha info:
    ```
    self._logger.warning(f"No HA info was found for edge {serial_number}. Skipping...")
    ```
  * If is not a raw ha state under monitoring
    ```
    self._logger.info(
                    f"HA partner for {serial_number} is in state {ha_state}, so HA will be considered as disabled for "
                    "this edge"
                )
    ```