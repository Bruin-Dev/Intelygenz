## Process ticket tasks without Triage note

```python
logger.info(f"Processing {len(ticket_details)} ticket tasks without Triage note...")
```

* For each task:
    ```python
    logger.info(f"Processing task of ticket {ticket_id} for edge {serial_number} without Triage note...")
    ```

    * If there is no status available for the edge:
      ```python
      logger.warning(
          f"No status was found for edge {serial_number} in the mapping between edges' serial numbers and "
          f"statuses. Skipping append Triage note to task of ticket {ticket_id}..."
      )
      ```
      _Continue with next task_

    * If the edge related to this task is no longer down:
      ```python
      logger.info(
          f"Edge {serial_number} is no longer down, so the initial Triage note won't be posted to ticket "
          f"{ticket_id}. Posting an Events note of the last 24 hours to the ticket so it's not blank..."
      )
      ```

        [_append_new_triage_notes_based_on_recent_events](_append_new_triage_notes_based_on_recent_events.md)

    * Otherwise:
        ```python
        logger.info(
            f"Edge {serial_number} is in {outage_type.value} state. Posting initial Triage note to ticket "
            f"{ticket_id}..."
        )
        ```

        * If the edge is the standby of a HA pair, and it's in Hard Down or Link Down state:
          ```python
          logger.info(
              f"Edge {serial_number} is down, but it doesn't qualify to be documented as a Service Outage in "
              f"ticket {ticket_id}. Most probable thing is that the edge is the standby of a HA pair, and "
              "standbys in outage state are only documented in the event of a Soft Down. Skipping..."
          )
          ```
          _Continue with next task_

        ```python
        logger.info(f"Getting events for edge {serial_number} in ticket {ticket_id}...")
        ```

        [VelocloudRepository::get_last_edge_events](../../repositories/velocloud_repository/get_last_edge_events.md)

        * If response status for get last edge events is not ok:
          ```python
          logger.error(
              f"Error while getting the last events of edge {serial_number}: {recent_events_response}. "
              f"Skipping append Triage note to task of ticket {ticket_id}..."
          )
          ```
          _Continue with next task_

        ```python
        logger.info(f"Building Triage note with {len(recent_events)} events from edge {serial_number}...")
        ```

        ```python
        logger.info(
            f"Appending Triage note with {len(recent_events)} events from edge {serial_number} to "
            f"ticket {ticket_id}..."
        )
        ```

        [BruinRepository::append_triage_note](../../repositories/bruin_repository/append_triage_note.md)

    ```python
    logger.info(f"Finished processing task of ticket {ticket_id} for edge {serial_number}!")
    ```

```python
logger.info(f"Finished processing {len(ticket_details)} ticket tasks without Triage note!")
```