## Get edges across all VCOs

* For every VCO:

    [get_edges_links_by_host](get_edges_links_by_host.md)

    * If an error occurred while fetching all edges in the VCO:
      ```python
      logger.warning(f"Error: could not retrieve edges links by host: {host}")
      ```
      _Continue with next VCO_