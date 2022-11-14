## Start reboot for DiGi links

```python
logger.info(f"Checking edge {serial_number} for DiGi Links")
```

* For each DiGi link:
    * If the DiGi link is down:
        ```python
        logger.info(f"Rebooting DiGi link {digi_link['interface_name']} from edge {serial_number}...")
        ```
  
        [DiGiRepository::reboot_link](../../repositories/digi_repository/reboot_link.md)
    
        * If response status for reboot DiGi link is not ok:
          ```python
          logger.error(
              f"Error while rebooting DiGi link {digi_link['interface_name']} from edge {serial_number}: "
              f"{reboot}. Skipping reboot for this link..."
          )
          ```
          _Continue with next DiGi link_
    
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
    
        * If response status for append DiGi Reboot note to ticket is not ok:
          ```python
          logger.error(
              f"Error while appending Reboot note to ticket {ticket_id} for DiGi link "
              f"{digi_link['interface_name']} from edge {serial_number}: {append_digi_reboot_note_response}"
          )
          ```
          _Continue with next DiGi link_
    
        ```python
        logger.info(
            f"Reboot note for DiGi link {digi_link['interface_name']} from edge {serial_number} "
            f"appended to ticket {ticket_id}!"
        )
        ```       

    * Otherwise:
      ```python
      logger.info(
          f"DiGi link {digi_link['interface_name']} from edge {serial_number} is not down. "
          f"Skipping reboot for this link..."
      )
      ```