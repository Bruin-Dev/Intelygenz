## Get edges for Triage

* For each VCO under monitoring:

    [get_links_with_edge_info](get_links_with_edge_info.md)

    * If response status for get links with edge info is not ok:
      ```python
      logger.error(f"Error while retrieving links with edge info for VeloCloud host {host}: {response}")
      ```
      _Continue with next VCO_

[group_links_by_edge](group_links_by_edge.md)