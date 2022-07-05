## Get all links metrics Documentation

* for host in self._config.MONITOR_CONFIG["velo_filter"]
    
    *[Gets links metrics by host](get_links_metrics_by_host.md)
    * if status from get_links_metrics_by_host return is not in range(200, 300)
      ```
      self._logger.info(f"Error: could not retrieve links metrics from Velocloud host {host}")
      ```