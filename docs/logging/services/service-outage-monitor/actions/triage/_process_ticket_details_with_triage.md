## Process ticket details with triage
```
self._logger.info("Processing ticket details with triage...")
```
* For detail in details:
  ```
  self._logger.info(f"Processing detail {ticket_detail_id} with triage of ticket {ticket_id}...")
  self._logger.info(
                f"Checking if events need to be appended to detail {ticket_detail_id} of ticket {ticket_id}..."
            )
  ```
  * If ticket note append recently:
    ```
    self._logger.info(
                    f"The last triage note was appended to detail {ticket_detail_id} of ticket "
                    f"{ticket_id} not long ago so no new triage note will be appended for now"
                )
    ```
  ```
  self._logger.info(f"Appending events to detail {ticket_detail_id} of ticket {ticket_id}...")
  ```
  * [_append_new_triage_notes_based_on_recent_events](_append_new_triage_notes_based_on_recent_events.md)
  ```
  self._logger.info(f"Events appended to detail {ticket_detail_id} of ticket {ticket_id}!")
  self._logger.info(f"Finished processing detail {ticket_detail_id} of ticket {ticket_id}!")
  ```
```
self._logger.info("Finished processing ticket details with triage!")
```