## Structure links metrics Documentation

* for link_info in links_metrics
  * if edge_state is None
    ```
    self._logger.info(
                    f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has an invalid state. Skipping..."
                )
    ```
  * if edge_state == "NEVER_ACTIVATED"
    ```
    self._logger.info(
                    f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has never been activated. Skipping..."
                )
    ```
    
