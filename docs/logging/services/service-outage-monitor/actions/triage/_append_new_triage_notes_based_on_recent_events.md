## Append new triage notes based on recent events
```
self._logger.info(f"Appending new triage note to detail {ticket_detail_id} of ticket {ticket_id}...")
self._logger.info(
            f"Getting events for serial {service_number} (detail {ticket_detail_id}) in ticket "
            f"{ticket_id} before applying triage..."
        )
```
* [get_last_edge_events](../../repositories/velocloud_repository/get_last_edge_events.md)
* If get last events status is not Ok:
  ```
  self._logger.warning(f"Bad status calling get last edge events for edge: {edge_full_id}. "
                                 f"Skipping append triage notes based in recent events ...")
  ```
* If not recent events:
  ```
  self._logger.info(
                f"No events were found for edge {service_number} starting from {events_lookup_timestamp}. "
                f"Not appending any new triage notes to detail {ticket_detail_id} of ticket {ticket_id}."
            )
  ```
* For chunk in event chunked:
  * If environment is PRODUCTION:
    * [append_note_to_ticket](../../repositories/bruin_repository/append_note_to_ticket.md)
    * If append note status is not Ok:
      ```
      self._logger.warning(f"Bad status apeending note to ticket: {ticket_id}. Skipping append note ...")
      ```
    ```
    self._logger.info(f"Triage appended to detail {ticket_detail_id} of ticket {ticket_id}!")
    ```
  * Else:
    ```
    self._logger.info(f"Triage appended to detail {ticket_detail_id} of ticket {ticket_id}!")
    ```   
* If note appended:
  * [_notify_triage_note_was_appended_to_ticket](_notify_triage_note_was_appended_to_ticket.md)