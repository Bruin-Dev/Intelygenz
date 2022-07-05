## Process email
* If not message or msg_uid = -1:
  ```
  self._logger.error(f"Invalid message: {email}")
  ```
```
self._logger.info(f"Processing email with msg_uid: {msg_uid} and subject: {subject}")
```
* If event in intermaper config up events:
  ```
  self._logger.info(
                f'Event from InterMapper was {parsed_email_dict["event"]}, there is no need to create '
                f"a new ticket. Checking for autoresolve ..."
            )
  ```
  * [_autoresolve_ticket](_autoresolve_ticket.md)
* If event in intermaper config down events:
  ```
  self._logger.info(
                f'Event from InterMapper was {parsed_email_dict["event"]}, '
                f'condition was {parsed_email_dict["condition"]}. Checking for ticket creation ...'
            )
  ```
  * If is piab device;
    ```
    self._logger.info(
                    f"The probe type from Intermapper is {parsed_email_dict['probe_type']}."
                    f"Attempting to get additional parameters from DRI..."
                )
    ```
    * [_get_dri_parameters](_get_dri_parameters.md)
  * [_create_outage_ticket](_create_outage_ticket.md)
* Else:
  ```
  self._logger.info(
                f'Event from InterMapper was {parsed_email_dict["event"]}, '
                f"so no further action is needs to be taken"
            )
  ```
* If event process successfully and environment is production:
  * [_mark_email_as_read](_mark_email_as_read.md)
* If even process successfully:
  ```
  self._logger.info(f"Processed email: {msg_uid}")
  ```
* Else:
  ```
  self._logger.error(
                f"Email with msg_uid: {msg_uid} and subject: {subject} "
                f"related to circuit ID: {circuit_id} could not be processed"
            )
  ```