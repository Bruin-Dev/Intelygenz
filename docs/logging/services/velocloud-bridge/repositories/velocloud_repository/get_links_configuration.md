## Get links configuration

[get_edge_configuration_modules](../../clients/velocloud_client/get_edge_configuration_modules.md)

* If response status for get edge configuration modules is not ok:
  ```python
  logger.error(
      f"Could not get links configuration for edge {edge_full_id}. Response: {config_modules_response}"
  )
  ```
  END

* If response does not have a `WAN` configuration module:
  ```python
  logger.warning(f"No WAN module was found for edge {edge_full_id}")
  ```
  END

* If `WAN` configuration module does not have links configurations:
  ```python
  logger.warning(f"No links configuration was found in WAN module of edge {edge_full_id}")
  ```
  END