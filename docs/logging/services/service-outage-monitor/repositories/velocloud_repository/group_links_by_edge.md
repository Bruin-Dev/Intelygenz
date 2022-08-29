## Process velocloud host Documentation

* for link in links
  * If not edge state:
    ```
    self._logger.info(
                    f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has an invalid state. Skipping..."
                )
    ```
  * If edge state is "NEVER_ACTIVATED"
    ```
    self._logger.info(
                    f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has never been activated. Skipping..."
                )
    ```

  * If link interface is not valid (i.e. `null`):
    ```
    self._logger.info(
        f"Link from edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} "
        f"(ID: {enterprise_id}) has a null interface, so it might have been decommissioned. Skipping..."
    )
    ```