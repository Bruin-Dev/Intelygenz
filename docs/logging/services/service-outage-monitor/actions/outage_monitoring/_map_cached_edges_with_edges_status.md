## Map cached edges with edges status Documentation
* for edge in edges:
  * If not edge status:
    ```
    self._logger.info(f'No edge status was found for cached edge {cached_edge["serial_number"]}. ' "Skipping...")
    ```
    * If host == metvco03.mettel.net and enterprise id == 124:
      ```
      self._logger.info(f"Edge {edge} was appended to the list of edges that have no status but"
                        f"are in the customer cache.")
      ```