## Check for failed reboots for DiGi links

* If the edge is under a Soft Down or Hard Down outage:
  ```python
  logger.info(
      f"Edge {serial_number} is not under a Link Down outage at this moment. "
      f"Skipping checking for failed DiGi reboots..."
  )
  ```
  END

```python
logger.info(f"Checking edge {serial_number} for DiGi Links")
```

* For each DiGi link:
    * If the DiGi link is down:
        ```python
        logger.info(
            f"Checking for failed reboots for DiGi link {digi_link['interface_name']} "
            f"from edge {serial_number}..."
        )
        ```
    
        [BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
    
        * If response status for get details of ticket is not ok:
          ```python
          logger.error(
              f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
              f"Skipping checking for failed DiGi reboots for this edge..."
          )
          ```
          END
    
        ```python
        logger.info(f"Notes of ticket {ticket_id} for edge {serial_number}: {notes_from_outage_ticket}")
        ```
    
        * If there is no DiGi Reboot note in this ticket:
          ```python
          logger.info(
              f"No DiGi note was found for ticket {ticket_id} and edge {serial_number}. "
              f"Skipping checking for failed DiGi reboots for this edge..."
          )
          ```
          END
    
        * If the last DiGi Reboot took place recently:
          ```python
          logger.info(
              f"The last DiGi reboot attempt for edge {serial_number} occurred "
              f'{self._config.MONITOR_CONFIG["last_digi_reboot_seconds"] / 60} or less minutes ago. '
              f"Skipping checking for failed DiGi reboots for this edge..."
          )
          ```
          END
    
        * If the DiGi Reboot note is related to the current DiGi link:
            ```python
            logger.info(
                f"Found DiGi Reboot note in ticket {ticket_id} for link {link_status['interface']} "
                f"from edge {serial_number}. "
                f"Since the link is still down, it's fair to assume the last DiGi reboot failed. "
                f"Checking to see if the ticket task for this edge should be forwarded to the Wireless team..."
            )
            ```
      
            * If there is a ticket note related to a forward to the Wireless team:
              ```python
              logger.info(
                  f"Task for edge {serial_number} from ticket {ticket_id} has already been forwarded "
                  f"to {target_queue}. Skipping forward..."
              )
              ```
              END
      
            ```python
            logger.info(
                f"Forwarding ticket task of {ticket_id} for edge {serial_number} to the Wireless team..."
            )
            ```
      
            [BruinRepository::change_detail_work_queue](../../repositories/bruin_repository/change_detail_work_queue.md)
      
            * If response status for forward ticket task to the Wireless team is not ok:
              ```python
              logger.error(
                  f"Error while forwarding ticket task of {ticket_id} for edge {serial_number} to "
                  f"the Wireless team: {change_detail_work_queue_response}."
              )
              ```
              END
      
            ```python
            logger.info(f"Ticket task of {ticket_id} for edge {serial_number} forwarded to the Wireless team!")
            ```
      
            [append_task_result_change_note](../../repositories/bruin_repository/append_task_result_change_note.md)

          * Otherwise:
            ```python
            logger.info(
                f"Found a DiGi Reboot note in ticket {ticket_id}, but it is not related to link "
                f"{link_status['interface']} from edge {serial_number}. "
                f"Attempting DiGi reboot for this link..."
            )
            ```
      
            [DiGiRepository::reboot_link](../../repositories/digi_repository/reboot_link.md)
      
            * If response status for reboot DiGi link is not ok:
              ```python
              logger.error(
                  f"Error while rebooting DiGi link {digi_link['interface_name']} from edge {serial_number}: "
                  f"{reboot}. Skipping reboot for this link..."
              )
              ```
              END
      
            ```python
            logger.info(f"DiGi link {digi_link['interface_name']} from edge {serial_number} rebooted!")
            ```
      
            ```python
            logger.info(
                f"Appending Reboot note for DiGi link {digi_link['interface_name']} from edge {serial_number} "
                f"to ticket {ticket_id}..."
            )
            ```
      
            [BruinRepository::append_digi_reboot_note](../../repositories/bruin_repository/append_digi_reboot_note.md)

    * Otherwise:
      ```python
      logger.info(
          f"DiGi link {digi_link['interface_name']} from edge {serial_number} is not down. "
          f"Skipping checking for failed DiGi reboot for this link..."
      )
      ```