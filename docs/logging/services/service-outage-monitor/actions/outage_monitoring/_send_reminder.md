## Send reminder
```
self._logger.info(f"Attempting to send reminder for service number {service_number} to ticket {ticket_id}")
```
* If not should reminder notification:
  ```
  self._logger.info(f"No Reminder note will be appended for service number {service_number} to ticket {ticket_id},"
                    f" since either the last documentation cycle started or the last reminder"
                    f" was sent too recently")
  ```
* If working environment not PRODUCTION:
  ```
  self._logger.info(f"No Reminder note will be appended for service number {service_number} to ticket {ticket_id} since "
                    f"the current environment is {working_environment.upper()}")
  ```
* [send_reminder_email_milestone_notification](../../repositories/bruin_repository/send_reminder_email_milestone_notification.md)
* If status not OK:
  ```
  self._logger.error(f"Reminder email of edge {service_number} could not be sent for ticket" f" {ticket_id}!")
  ```
* [_append_reminder_note](_append_reminder_note.md)
* If status to append reminder note not Ok:
  ```
  self._logger.error(f"Reminder note of edge {service_number} could not be appended to ticket" f" {ticket_id}!")
  ```
```
self._logger.error(f"Reminder note of edge {service_number} was successfully appended to ticket" f" {ticket_id}!")
```