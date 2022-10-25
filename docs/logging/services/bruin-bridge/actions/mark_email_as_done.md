## Subject: bruin.mark.email.done

_Message arrives at subject_

* If message body has `email_id`:
  ```python
  self._logger.info(f"Marking email: {email_id} as Done")
  ```
  [mark_email_as_done](../repositories/bruin_repository/mark_email_as_done.md)

* else
  ```python
  self._logger.error(f"Cannot mark emails as done using {json.dumps(msg)}. JSON malformed")
  ```

  END