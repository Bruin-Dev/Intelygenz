## Map edges' data from the cache with their current status

* For each edge:
    * If VeloCloud did not include the status of the edge in the response:
      ```python
      logger.warning(f'No edge status was found for cached edge {cached_edge["serial_number"]}. Skipping...')
      ```