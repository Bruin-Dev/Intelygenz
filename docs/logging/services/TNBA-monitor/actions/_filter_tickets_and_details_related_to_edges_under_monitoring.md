## Filter tickets and details related to edges under monitoring
* for ticket in tickets
  * If not relevant ticket:
    ```
    self._logger.warning(f"Don't found relevant tickets. Skipping ticket ...")
    ```