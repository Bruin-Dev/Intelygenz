## Check for digi reboot
```
self._logger.info(f"Checking edge {serial_number} for DiGi Links")
```
* [reboot_link](../../repositories/digi_repository/reboot_link.md)
* If status of reboot link is not Ok:
  ```
  self._logger.info(f'Attempting DiGi reboot of link with MAC address of {digi_link["logical_id"]}'
                        f"in edge {serial_number}")
  ```
  * [append_digi_reboot_note](../../repositories/bruin_repository/append_digi_reboot_note.md)
  * If status not Ok:
    ```
    self._logger.warning(f" Bad status calling to append digi reboot note. Can't append the note")
    ```