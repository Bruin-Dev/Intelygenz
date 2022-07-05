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