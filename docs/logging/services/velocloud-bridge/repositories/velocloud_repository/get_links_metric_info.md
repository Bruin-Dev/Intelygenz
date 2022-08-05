## Get links metric info

[get_links_metric_info](../../clients/velocloud_client/get_links_metric_info.md)

* If response status for get links metric info is not ok:
  ```python
  logger.error(
      f"Could not get links metric info for host {velocloud_host} and interval {interval}. Response: "
      f"{links_metric_info_response}"
  )
  ```
  END