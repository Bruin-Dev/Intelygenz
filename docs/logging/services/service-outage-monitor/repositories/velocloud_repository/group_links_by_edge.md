## Group links by edge, and filter out links with edges that shouldn't be monitored

* For each raw link:

    * If the state of the link's edge is invalid:
      ```python
      logger.warning(
          f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
          f"has an invalid state. Skipping..."
      )
      ```
      _Continue with next raw link_

    * If the link's edge has never been activated:
      ```python
      logger.warning(
          f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
          f"has never been activated. Skipping..."
      )
      ```
      _Continue with next raw link_
  
    _Raw link is grouped by edge_

