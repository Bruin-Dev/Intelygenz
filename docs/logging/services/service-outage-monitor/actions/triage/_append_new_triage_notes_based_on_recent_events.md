## Append new Events note based on recent events to ticket

```python
logger.info(f"Appending new triage note to task of ticket {ticket_id} for edge {service_number}...")
```

```python
logger.info(f"Getting events for edge {service_number} in ticket {ticket_id}...")
```

[VelocloudRepository::get_last_edge_events](../../repositories/velocloud_repository/get_last_edge_events.md)

* If response status for get last edge events is not ok:
  ```python
  logger.error(
      f"Error while getting the last events for edge {service_number}: {recent_events_response}. "
      f"Skipping append Events note to ticket {ticket_id}..."
  )
  ```
  END

* If no events were found:
  ```python
  logger.info(
      f"No events were found for edge {service_number} starting from {events_lookup_timestamp}. "
      f"Skipping append Events note to ticket {ticket_id}..."
  )
  ```
  END

_The whole data set of edge events is split to multiple chunks_

* For each chunk:
    ```python
    logger.info(f"Building Events note with {len(chunk)} events from edge {service_number}...")
    ```

    ```python
    logger.info(
        f"Appending Events note with {len(chunk)} events from edge {service_number} to "
        f"ticket {ticket_id}..."
    )
    ```

    [BruinRepository::append_note_to_ticket](../../repositories/bruin_repository/append_note_to_ticket.md)

    * If response status for append Events note to ticket is not ok:
      ```python
      logger.error(
          f"Error while appending Events note with {len(chunk)} events from edge {service_number} to "
          f"ticket {ticket_id}: {response}"
      )
      ```
      _Continue with next chunk_

    ```python
    logger.info(
        f"Events note with {len(chunk)} events from edge {service_number} appended to ticket {ticket_id}!"
    )
    ```