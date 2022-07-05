## Attempt forward to asr

```
self._logger.info(f"Attempting to forward task of ticket {ticket_id} related to serial {serial_number} to ASR Investigate...")
```
* If faulty edge:
  ```
  self._logger.info(f"Outage of serial {serial_number} is caused by a faulty edge. Related detail of ticket {ticket_id} "
                "will not be forwarded to ASR Investigate.")
  ```
```
self._logger.info(f"Searching serial {serial_number} for any wired links")
```
* If not wired links:
  ```
  self._logger.info(f"No wired links are disconnected for serial {serial_number}. Related detail of ticket {ticket_id} "
                "will not be forwarded to ASR Investigate.")
  ```
```
self._logger.info(f"Filtering out any of the wired links of serial {serial_number} that contains any of the "
            f'following: {self._config.MONITOR_CONFIG["blacklisted_link_labels_for_asr_forwards"]} '
            f"in the link label")
```
* If not whitelist links:
  ```
  self._logger.info(f"No links with whitelisted labels were found for serial {serial_number}. "
                    f"Related detail of ticket {ticket_id} will not be forwarded to ASR Investigate.")
  ```
* [get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
* If status not Ok:
  ```
  self._logger.info(f"Bad status calling get ticket details. Skipping forward asr ...")
  ```
```
self._logger.info(f"Notes of ticket {ticket_id}: {notes_from_outage_ticket}")
```
* If task result note:
  ```
  self._logger.info(f"Detail related to serial {serial_number} of ticket {ticket_id} has already been forwarded to "
                    f'"{target_queue}"')
  ```
* [change_detail_work_queue](../../repositories/bruin_repository/change_detail_work_queue.md)
* If status of change detail work queue in Ok:
  * [append_asr_forwarding_note](../../repositories/bruin_repository/append_asr_forwarding_note.md)