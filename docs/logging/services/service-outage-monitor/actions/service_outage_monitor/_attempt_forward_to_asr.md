## Forward ticket task to ASR

```python
logger.info(
    f"Attempting to forward task of ticket {ticket_id} related to serial {serial_number} to ASR Investigate..."
)
```

* If the edge is under a Soft Down or Hard Down outage:
  ```python
  logger.info(
      f"Outage of edge {serial_number} is caused by a faulty edge. Related task of ticket {ticket_id} "
      "will not be forwarded to ASR Investigate."
  )
  ```
  END

```python
logger.info(f"Searching for any disconnected wired links in edge {serial_number}...")
```

* If there are no disconnected wired links for this edge:
  ```python
  logger.info(
      f"No wired links are disconnected for edge {serial_number}. Related task of ticket {ticket_id} "
      "will not be forwarded to ASR Investigate."
  )
  ```
  END

```python
logger.info(
    f"Filtering out any of the wired links of edge {serial_number} that contains any of the "
    f'following: {self._config.MONITOR_CONFIG["blacklisted_link_labels_for_asr_forwards"]} '
    f"in the link label"
)
```

* If all the disconnected wired links have a label blacklisted from ASR forwards:
  ```python
  logger.info(
      f"No links with whitelisted labels were found for edge {serial_number}. "
      f"Related task of ticket {ticket_id} will not be forwarded to ASR Investigate."
  )
  ```
  END

[BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

* If response status for get ticket details is not ok:
  ```python
  logger.error(f"Error while getting details of ticket {ticket_id}. Skipping forward to ASR...")
  ```
  END

```python
logger.info(f"Notes of ticket {ticket_id} for edge {serial_number}: {notes_from_outage_ticket}")
```

* If there is a ticket note related to a forward to ASR:
  ```python
  logger.info(
      f"Task related to edge {serial_number} of ticket {ticket_id} has already been forwarded to "
      f'"{target_queue}"'
  )
  ```
  END

```python
logger.info(f"Forwarding task from ticket {ticket_id} related to edge {serial_number} to ASR...")
```

[BruinRepository::change_detail_work_queue](../../repositories/bruin_repository/change_detail_work_queue.md)

* If response status for forward ticket task to ASR is not ok:
  ```python
  logger.error(
      f"Error while forwarding ticket task of {ticket_id} for edge {serial_number} to "
      f"ASR: {change_detail_work_queue_response}."
  )
  ```
  END

```python
logger.info(f"Ticket task of {ticket_id} for edge {serial_number} forwarded to ASR!")
```

[BruinRepository::append_asr_forwarding_note](../../repositories/bruin_repository/append_asr_forwarding_note.md)