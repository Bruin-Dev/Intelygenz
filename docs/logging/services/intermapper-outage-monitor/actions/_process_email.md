## Process E-mail

* If message is undefined or its UID is `-1`:
  ```python
  logger.error(f"Invalid message: {email}")
  ```
  END

```python
logger.info(f"Processing email with msg_uid: {msg_uid} and subject: {subject}")
```

* If e-mail represents an UP event:
  ```python
  logger.info(
      f'Event from InterMapper was {parsed_email_dict["event"]}, there is no need to create '
      f"a new ticket. Checking for autoresolve ..."
  )
  ```
  [_autoresolve_ticket](_autoresolve_ticket.md)

* If e-mail represents a DOWN event:
  ```python
  logger.info(
      f'Event from InterMapper was {parsed_email_dict["event"]}, '
      f'condition was {parsed_email_dict["condition"]}. Checking for ticket creation ...'
  )
  ```

    * If device is a PIAB:
      ```python
      logger.info(
          f"The probe type from Intermapper is {parsed_email_dict['probe_type']}."
          f"Attempting to get additional parameters from DRI..."
      )
      ```
      [_get_dri_parameters](_get_dri_parameters.md)

    [_create_outage_ticket](_create_outage_ticket.md)

* If e-mail represents any other kind of event:
  ```python
  logger.info(
      f'Event from InterMapper was {parsed_email_dict["event"]}, '
      f"so no further action is needs to be taken"
  )
  ```

* If e-mail was processed successfully and environment is `PRODUCTION`:
    * [_mark_email_as_read](_mark_email_as_read.md)

* If event was processed successfully:
  ```python
  logger.info(f"Processed email: {msg_uid}")
  ```
* Otherwise:
  ```python
  logger.error(
      f"Email with msg_uid: {msg_uid} and subject: {subject} "
      f"related to service number: {service_number} could not be processed"
  )
  ```