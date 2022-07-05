## Process email batch
```
self._logger.info(f"Processing {len(emails)} email(s) with asset_id {asset_id}...")
```
* If not asset id or asset id = SD-WAN:
  * for email in emails:
    * [mark email as read](../repositories/notifications_repository/mark_email_as_read.md)
  ```
  self._logger.info(f"Invalid asset_id. Skipping emails with asset_id {asset_id}...")
  ```
* [get_circuit_id](../repositories/bruin_repository/get_circuit_id.md)
* If status not Ok:
  ```
  self._logger.error(f"Failed to get circuit id. Skipping emails with asset_id {asset_id}...")
  ```
* If status = 204:
  ```
  self._logger.error(
                    f"Bruin returned a 204 when getting the circuit id of asset_id {asset_id}. "
                    f"Marking all emails with this asset_id as read"
                )
  ```
* [_process_email](_process_email.md)
```
self._logger.info(f"Finished processing all emails with asset_id {asset_id}!")
```