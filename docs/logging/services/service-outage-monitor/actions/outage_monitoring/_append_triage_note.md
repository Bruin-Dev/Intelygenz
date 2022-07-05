## Append triage note
* [get_last_edge_events](../../repositories/velocloud_repository/get_last_edge_events.md)
  * If status not OK:
    ```
    self._logger.warning(f"Don't found last edge events for edge id: {edge_full_id}. Skipping append triage "
                         f"note ...")
    ```
* [get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
* If status not OK:
    ```
    self._logger.warning(f"Don't found ticket details for ticket id: {ticket_id}. Skipping append triage "
                         f"note ...")
    ```
* [build_triage_note](../../repositories/triage_repository/build_triage_note.md)
```
self._logger.info(f"Appending triage note to detail {ticket_detail_id} (serial {serial_number}) of ticket 
{ticket_id}...")
```
* [append_triage_note](../../repositories/bruin_repository/append_triage_note.md)