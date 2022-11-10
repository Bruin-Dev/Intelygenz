## Attempt forward of ticket task to ASR

* If no ticket was created, re-opened or updated while monitoring the link:
  ```python
  logger.warning(
      f"No ticket could be created, re-opened or updated for edge {serial_number} and link {interface}. "
      f"Skipping forward to ASR..."
  )
  ```
  END

```python
logger.info(
    f"Attempting to forward task of ticket {ticket_id} related to serial {serial_number} to ASR Investigate..."
)
```

* If link type is Wired:
    ```python
    logger.warning(
        f"Link {interface} is of type {link_interface_type} and not WIRED. Attempting to forward to HNOC..."
    )
    ```

    [_schedule_forward_to_hnoc_queue](_schedule_forward_to_hnoc_queue.md)

    _Ticket task is immediately forwarded to HNOC_

    END

```python
logger.info(
    f"Filtering out any of the wired links of serial {serial_number} that contains any of the following: "
    f"{self._config.MONITOR_CONFIG['blacklisted_link_labels_for_asr_forwards']} in the link label"
)
```

* If link is BYOB, Client Owned or a PIAB, or its label is an IP address:
  ```python
  logger.warning(
      f"No links with whitelisted labels were found for serial {serial_number}. "
      f"Related detail of ticket {ticket_id} will not be forwarded to {target_queue}."
  )
  ```
  END

[BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

* If response status for get ticket details is not ok:
  ```python
  logger.error(
      f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. Skipping autoresolve..."
  )
  ```
  END

* If troubles other than Circuit Instability have already been reported to this ticket:
  ```python
  logger.warning(
      f"Other service affecting troubles were found in ticket id {ticket_id}. Skipping forward to ASR..."
  )
  ```
  END

* If the ticket task has been previously forwarded to ASR:
  ```python
  logger.warning(
      f"Detail related to serial {serial_number} of ticket {ticket_id} has already been forwarded to "
      f'"{task_result}"'
  )
  ```
  END

[BruinRepository::change_detail_work_queue](../../repositories/bruin_repository/change_detail_work_queue.md)

* If response status for change detail work queue is ok:
  [BruinRepository::append_asr_forwarding_note](../../repositories/bruin_repository/append_asr_forwarding_note.md)