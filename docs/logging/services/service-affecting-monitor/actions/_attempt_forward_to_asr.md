## Attempt forward to asr Documentation

```
self._logger.info(
            f"Attempting to forward task of ticket {ticket_id} related to serial {serial_number} to ASR Investigate..."
        )
```

* if link_interface_type != "WIRED"
  ```
  self._logger.info(
                f"Link {interface} is of type {link_interface_type} and not WIRED. Attempting to forward " f"to HNOC..."
            )
  ```
  * [Forward ticket to hnoc queue](_forward_ticket_to_hnoc_queue.md)

```
self._logger.info(
            f"Filtering out any of the wired links of serial {serial_number} that contains any of the "
            f"following: "
            f'{self._config.ASR_CONFIG["link_labels_blacklist"]} '
            f"in the link label"
        )
```

* if not _should_be_forwarded_to_asr
  ```
  self._logger.info(
                f"No links with whitelisted labels were found for serial {serial_number}. "
                f"Related detail of ticket {ticket_id} will not be forwarded to {target_queue}."
            )
  ```

* [Get ticket details](../repositories/bruin_repository/get_ticket_details.md)

* if other_troubles_in_ticket
 ```
 self._logger.info(
                f"Other service affecting troubles were found in ticket id {ticket_id}. Skipping forward" f"to asr..."
            )
 ```

* if task_result_note is not None
  ```
  self._logger.info(
                f"Detail related to serial {serial_number} of ticket {ticket_id} has already been forwarded to "
                f'"{task_result}"'
            )
  ```
* [Change detail work queue](../repositories/bruin_repository/change_detail_work_queue.md)
* [Append asr forwarding note](../repositories/bruin_repository/append_asr_forwarding_note_to_ticket.md)

