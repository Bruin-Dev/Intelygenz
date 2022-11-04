## Get logical ID for all links belonging to an edge

* For each VCO:

    * For each enterprise within the VCO:

        [_get_all_enterprise_edges](_get_all_enterprise_edges.md)

        * If response status for get all edges in an enterprise is not ok:
          ```python
          logger.error(f"Error could not get enterprise edges of enterprise {enterprise}")
          ```
          _Continue with next enterprise_