## Process ticket details without triage
```
self._logger.info("Processing ticket details without triage...")
```
* For detail in details:
  ```
  self._logger.info(f"Processing detail {ticket_detail_id} without triage of ticket {ticket_id}...")
  ```
  * If not outage type:
    ```
    self._logger.info(
                    f"Edge {serial_number} is no longer down, so the initial triage note won't be posted to ticket "
                    f"{ticket_id}. Posting events of the last 24 hours to the ticket so it's not blank..."
                )
    ``` 
    * [_append_new_triage_notes_based_on_recent_events](_append_new_triage_notes_based_on_recent_events.md)
  * Else:
    ```
    self._logger.info(
                    f"Edge {serial_number} is in {outage_type.value} state. Posting initial triage note to ticket "
                    f"{ticket_id}..."
                )
    ```
    * If not document outage:
      ```
      self._logger.info(
                        f"Edge {serial_number} is down, but it doesn't qualify to be documented as a Service Outage in "
                        f"ticket {ticket_id}. Most probable thing is that the edge is the standby of a HA pair, and "
                        "standbys in outage state are only documented in the event of a Soft Down. Skipping..."
                    )
      ```
    * [get_last_edge_events](../../repositories/velocloud_repository/get_last_edge_events.md)
    * If get last edge events not Ok:
      ```
      self._logger.warning(f"Bad status calling to get last edge events. "
      f"Skipping process details without details ...")
      ```
  ```
  self._logger.info(f"Finished processing detail {ticket_detail_id} of ticket {ticket_id}!")
  ```  
```
self._logger.info("Finished processing ticket details without triage!")
```  