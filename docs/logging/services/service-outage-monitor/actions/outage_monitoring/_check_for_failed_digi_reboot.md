## Check for failed digi reboot
```
self._logger.info(f"Checking edge {serial_number} for DiGi Links")
```
* for link in digi_links:
  * [get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
  * If status is not Ok:
    ```
    self._logger.info(f"Bad status calling to get ticket details checking failed digi reboot."
                      f" Skipping link ...")
    ```
  * If not find digi note:
    ```
    self._logger.info(f"No DiGi note was found for ticket {ticket_id}")
    ```
  * If rebooted recently:
    ```
    self._logger.info(f"The last DiGi reboot attempt for Edge {serial_number} did not occur "
                      f'{self._config.MONITOR_CONFIG["last_digi_reboot_seconds"] / 60} or more mins ago.')
    ```
  * If interface note is same that link:
    * If not find wireless:
      ```
      self._logger.info(f'Task results has already been changed to "{target_queue}"')
      ```
    * [change_detail_work_queue](../../repositories/bruin_repository/change_detail_work_queue.md)
    * If status Ok:
      * [append_task_result_change_note](../../repositories/bruin_repository/append_task_result_change_note.md)
    * Else:
      * [reboot_link](../../repositories/digi_repository/reboot_link.md)
      * If reboot link status Ok:
        ```
        self._logger.info(f'Attempting DiGi reboot of link with MAC address of {digi_link["logical_id"]}'
                            f"in edge {serial_number}")
        ```
        * [append_digi_reboot_note](../../repositories/bruin_repository/append_digi_reboot_note.md)