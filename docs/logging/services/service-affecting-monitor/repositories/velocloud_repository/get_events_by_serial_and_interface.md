## Get events by serial and interface Documentation

* for host in edges_by_host_and_enterprise
  
  * for enterprise_id in edges_by_enterprise
    
    * [Get enterprise events](get_enterprise_events.md)
    * for event in enterprise_events
      
      * if not matching_edge
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