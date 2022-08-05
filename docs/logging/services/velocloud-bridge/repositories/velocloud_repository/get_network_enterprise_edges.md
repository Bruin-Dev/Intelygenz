## Get network enterprise edges

[get_network_enterprises](../../clients/velocloud_client/get_network_enterprises.md)

* If response status for get network enterprises is not ok:
  ```python
  logger.error(
      f"Could not get network enterprise edges for host {host} and enterprises {enterprise_ids}. Response: "
      f"{enterprise_edges_response}"
  )
  ```
  END

* If the list of enterprises from the response is empty:
  ```python
  logger.warning(f"No enterprises found for host {host} and enterprise ids {enterprise_ids}")
  ```
  END

* If enterprises have edges associated:
  ```python
  logger.info(f"Found {len(edges)} edges for host {host} and enterprise ids {enterprise_ids}")
  ```
* Otherwise:
  ```python
  logger.warning(f"No edges found for host {host} and enterprise ids {enterprise_ids}")
  ```
