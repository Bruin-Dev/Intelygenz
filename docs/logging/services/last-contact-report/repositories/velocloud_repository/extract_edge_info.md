## Extract edge info from links with edge info

* For link in links with edge info:
    * If the state of the edge bound to the link is invalid:
      ```python
      logger.info(
          f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
          f"has an invalid state. Skipping..."
      )
      ```
      _Continue with next link with edge info_

    * If the edge bound to the link has never been activated:
      ```python
      logger.info(
          f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
          f"has never been activated. Skipping..."
      )
      ```
      _Continue with next link with edge info_
