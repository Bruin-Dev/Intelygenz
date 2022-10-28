## Subject: bruin.link.ticket.email

_Message arrives at subject_

* If message body doesn't have `ticket_id` or `email_id`:
  ```python
  logger.error(f"Cannot link ticket to email using {json.dumps(msg)}. JSON malformed")
  ```
  END

```python
logger.info(f"Linking ticket {ticket_id} to email {email_id}...")
```

[link_ticket_to_email](../repositories/bruin_repository/link_ticket_to_email.md)

```python
logger.info(f"Ticket {ticket_id} successfully posted to email_id:{email_id} ")
```
