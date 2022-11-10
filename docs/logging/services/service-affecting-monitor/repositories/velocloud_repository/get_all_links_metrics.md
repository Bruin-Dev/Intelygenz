## Get all links metrics

* For each VCO under monitoring:

    [get links metrics by host](get_links_metrics_by_host.md)

    * If response status for get links metrics by VeloCloud host (VCO) is not ok:
      ```python
      logger.info(f"Error: could not retrieve links metrics from Velocloud host {host}")
      ```
      _Continue with next VeloCloud host_