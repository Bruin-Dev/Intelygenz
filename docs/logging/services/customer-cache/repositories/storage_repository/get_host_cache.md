## Get customer caches for VeloCloud hosts (VCOs)

* If VeloCloud hosts' filter is empty:
  ```python
  logger.info("No VeloCloud hosts' filter was specified. Fetching caches for all hosts...")
  ```
* Otherwise:
  ```python
  logger.info(f"Fetching caches for VeloCloud hosts: {filters.keys()}...")
  ```

  * For each VCO specified in the filter:

      [get_cache](get_cache.md)

      * If the filter specified a subset of enterprises from the VCO:
        ```python
        logger.info(f"Filtering {host} cache of {len(host_cache)} edges for enterprises: {filters[host]}...")
        ```

        _Cache is filtered_

        ```python
        logger.info(f"Cache for host {host} and filtered by enterprises has {len(host_cache)} edges")
        ```