## Get VeloCloud events for edge and group them by interfaces (links)

[_structure_edges_by_host_and_enterprise](_structure_edges_by_host_and_enterprise.md)

* For each VeloCloud host (VCO):
    * For each enterprise in the VCO:

        [get_enterprise_events](get_enterprise_events.md)

        * If response status for get enterprise events is not ok:
          ```python
          logger.error(
              f"Error while getting enterprise events for host {host} and enterprise {enterprise_id}: "
              f"{enterprise_events_response}"
          )
          ```
          _Continue with next enterprise_

        * For each event found for the enterprise:

            * If there's no edge in the cache of customers whose name matches the one included in the event:
              ```python
              logger.info(f'No edge in the customer cache had edge name {event["edgeName"]}. Skipping...')
              ```
              _Continue with next event_

            ```python
            logger.info(
                f'Event with edge name {event["edgeName"]} matches edge from customer cache with'
                f"serial number {serial}"
            )
            ```