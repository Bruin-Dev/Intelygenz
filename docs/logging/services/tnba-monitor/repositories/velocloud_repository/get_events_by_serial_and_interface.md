## Get events by serial and interface
* for host in hosts: 
  * for enterprise id in enterprises ids:
  * [get_enterprise_events](get_enterprise_events.md)
    ```
    self._logger.warning(f" Bad status calling get enterprise events for host: {host} and enterprise"
                                         f"{enterprise_id}. Skipping enterprise events ...")
    ```
  * For events in enterprise events:
    * If not match edge:
      ```
      self._logger.info(
                            f'No edge in the customer cache had edge name {event["edgeName"]}. Skipping...'
                        )
      ```
    ```
    self._logger.info(
                        f'Event with edge name {event["edgeName"]} matches edge from customer cache with'
                        f"serial number {serial}"
                    )
    ```